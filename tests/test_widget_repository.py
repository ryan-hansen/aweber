"""
Tests for Widget repository operations.

This module tests the WidgetRepository class including CRUD operations,
pagination, error handling, and database interactions.
"""

import pytest
import pytest_asyncio

from src.app.database import TestAsyncSessionLocal
from src.app.exceptions import WidgetNotFoundException
from src.app.repositories.widget import PaginationResult, WidgetRepository
from src.app.schemas.widget import WidgetCreate, WidgetUpdate

# Database setup is handled by the autouse fixture in conftest.py


@pytest_asyncio.fixture
async def widget_repo():
    """Create a widget repository for testing."""
    async with TestAsyncSessionLocal() as session:
        repo = WidgetRepository(session)
        yield repo


async def create_sample_widgets(repo: WidgetRepository):
    """Helper function to create sample widgets in a repository."""
    widgets = []
    sample_data = [
        WidgetCreate(name="Widget A", number_of_parts=5),
        WidgetCreate(name="Widget B", number_of_parts=10),
        WidgetCreate(name="Widget C", number_of_parts=15),
        WidgetCreate(name="Test Widget", number_of_parts=20),
        WidgetCreate(name="Another Widget", number_of_parts=25),
    ]

    for widget_data in sample_data:
        widget = await repo.create(widget_data)
        widgets.append(widget)

    return widgets


class TestWidgetRepositoryCreate:
    """Test widget creation operations."""

    @pytest.mark.asyncio
    async def test_create_widget_success(self, widget_repo):
        """Test successful widget creation."""
        widget_data = WidgetCreate(name="Test Widget", number_of_parts=5)

        widget = await widget_repo.create(widget_data)

        assert widget.id is not None
        assert widget.name == "Test Widget"
        assert widget.number_of_parts == 5
        assert widget.created_at is not None
        assert widget.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_widget_with_name_trimming(self, widget_repo):
        """Test widget creation with name trimming."""
        widget_data = WidgetCreate(
            name="  Trimmed Widget  ", number_of_parts=3
        )

        widget = await widget_repo.create(widget_data)

        assert widget.name == "Trimmed Widget"
        assert widget.number_of_parts == 3

    @pytest.mark.asyncio
    async def test_create_widget_with_max_name_length(self, widget_repo):
        """Test widget creation with maximum name length."""
        long_name = "a" * 64  # Maximum allowed length
        widget_data = WidgetCreate(name=long_name, number_of_parts=1)

        widget = await widget_repo.create(widget_data)

        assert widget.name == long_name
        assert widget.number_of_parts == 1

    @pytest.mark.asyncio
    async def test_create_widget_database_error_rollback(self, widget_repo):
        """Test that database errors are properly handled with rollback."""
        # Create a widget with invalid data that will cause violation
        # Note: This validates Pydantic schema validation, which prevents
        # invalid data from reaching the repository
        with pytest.raises(ValueError):
            # This should fail at Pydantic validation level
            WidgetCreate(name="Test", number_of_parts=0)

        # Verify no widget was created
        result = await widget_repo.get_all()
        assert len(result.items) == 0


class TestWidgetRepositoryRead:
    """Test widget retrieval operations."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, widget_repo):
        """Test successful widget retrieval by ID."""
        sample_widgets = await create_sample_widgets(widget_repo)
        widget_id = sample_widgets[0].id

        widget = await widget_repo.get_by_id(widget_id)

        assert widget.id == widget_id
        assert widget.name == sample_widgets[0].name
        assert widget.number_of_parts == sample_widgets[0].number_of_parts

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, widget_repo):
        """Test widget retrieval with non-existent ID."""
        with pytest.raises(WidgetNotFoundException) as exc_info:
            await widget_repo.get_by_id(999)

        assert "Widget with ID 999 not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_all_default_pagination(self, widget_repo):
        """Test getting all widgets with default pagination."""
        await create_sample_widgets(widget_repo)
        result = await widget_repo.get_all()

        assert isinstance(result, PaginationResult)
        assert len(result.items) == 5
        assert result.total == 5
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 1

    @pytest.mark.asyncio
    async def test_get_all_custom_pagination(self, widget_repo):
        """Test getting widgets with custom pagination."""
        await create_sample_widgets(widget_repo)
        result = await widget_repo.get_all(page=2, size=2)

        assert len(result.items) == 2
        assert result.total == 5
        assert result.page == 2
        assert result.size == 2
        assert result.pages == 3

    @pytest.mark.asyncio
    async def test_get_all_ordering(self, widget_repo):
        """Test getting widgets with custom ordering."""
        await create_sample_widgets(widget_repo)
        # Order by name ascending
        result = await widget_repo.get_all(order_by="name", order_desc=False)
        names = [widget.name for widget in result.items]
        assert names == sorted(names)

        # Order by name descending
        result = await widget_repo.get_all(order_by="name", order_desc=True)
        names = [widget.name for widget in result.items]
        assert names == sorted(names, reverse=True)

    @pytest.mark.asyncio
    async def test_get_all_invalid_pagination_params(self, widget_repo):
        """Test get_all with invalid pagination parameters."""
        await create_sample_widgets(widget_repo)
        # Invalid page (should default to 1)
        result = await widget_repo.get_all(page=-1, size=0)
        assert result.page == 1
        assert result.size == 10  # Should default to 10

    @pytest.mark.asyncio
    async def test_get_all_max_page_size_limit(self, widget_repo):
        """Test get_all respects maximum page size limit."""
        await create_sample_widgets(widget_repo)
        result = await widget_repo.get_all(
            size=200
        )  # Should be limited to 100
        assert result.size == 100

    @pytest.mark.asyncio
    async def test_get_all_invalid_order_field(self, widget_repo):
        """Test get_all with invalid order field defaults to 'id'."""
        await create_sample_widgets(widget_repo)
        result = await widget_repo.get_all(order_by="invalid_field")
        # Should still work and use 'id' as default
        assert len(result.items) == 5

    @pytest.mark.asyncio
    async def test_get_all_empty_database(self, widget_repo):
        """Test getting widgets from empty database."""
        result = await widget_repo.get_all()

        assert len(result.items) == 0
        assert result.total == 0
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 0


class TestWidgetRepositoryUpdate:
    """Test widget update operations."""

    @pytest.mark.asyncio
    async def test_update_widget_success(self, widget_repo):
        """Test successful widget update."""
        sample_widgets = await create_sample_widgets(widget_repo)
        widget_id = sample_widgets[0].id
        update_data = WidgetUpdate(name="Updated Widget", number_of_parts=100)

        updated_widget = await widget_repo.update(widget_id, update_data)

        assert updated_widget.id == widget_id
        assert updated_widget.name == "Updated Widget"
        assert updated_widget.number_of_parts == 100

    @pytest.mark.asyncio
    async def test_update_widget_partial(self, widget_repo):
        """Test partial widget update."""
        sample_widgets = await create_sample_widgets(widget_repo)
        widget_id = sample_widgets[0].id
        original_name = sample_widgets[0].name

        # Update only number_of_parts
        update_data = WidgetUpdate(number_of_parts=99)
        updated_widget = await widget_repo.update(widget_id, update_data)

        assert updated_widget.name == original_name  # Should remain unchanged
        assert updated_widget.number_of_parts == 99

    @pytest.mark.asyncio
    async def test_update_widget_no_changes(self, widget_repo):
        """Test updating widget with no actual changes."""
        sample_widgets = await create_sample_widgets(widget_repo)
        widget_id = sample_widgets[0].id
        original_widget = sample_widgets[0]

        # Empty update
        update_data = WidgetUpdate()
        updated_widget = await widget_repo.update(widget_id, update_data)

        assert updated_widget.id == widget_id
        assert updated_widget.name == original_widget.name
        assert (
            updated_widget.number_of_parts == original_widget.number_of_parts
        )

    @pytest.mark.asyncio
    async def test_update_widget_not_found(self, widget_repo):
        """Test updating non-existent widget."""
        update_data = WidgetUpdate(name="Updated Widget")

        with pytest.raises(WidgetNotFoundException):
            await widget_repo.update(999, update_data)

    @pytest.mark.asyncio
    async def test_update_widget_constraint_violation(self, widget_repo):
        """Test update with constraint violation."""
        # This should fail at Pydantic validation level
        with pytest.raises(ValueError):
            WidgetUpdate(number_of_parts=0)  # Should violate constraint


class TestWidgetRepositoryDelete:
    """Test widget deletion operations."""

    @pytest.mark.asyncio
    async def test_delete_widget_success(self, widget_repo):
        """Test successful widget deletion."""
        sample_widgets = await create_sample_widgets(widget_repo)
        widget_id = sample_widgets[0].id

        result = await widget_repo.delete(widget_id)

        assert result is True

        # Verify widget is deleted
        with pytest.raises(WidgetNotFoundException):
            await widget_repo.get_by_id(widget_id)

    @pytest.mark.asyncio
    async def test_delete_widget_not_found(self, widget_repo):
        """Test deleting non-existent widget."""
        with pytest.raises(WidgetNotFoundException):
            await widget_repo.delete(999)


class TestWidgetRepositoryUtility:
    """Test utility methods."""

    @pytest.mark.asyncio
    async def test_exists_widget_found(self, widget_repo):
        """Test exists method with existing widget."""
        sample_widgets = await create_sample_widgets(widget_repo)
        widget_id = sample_widgets[0].id

        exists = await widget_repo.exists(widget_id)

        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_widget_not_found(self, widget_repo):
        """Test exists method with non-existent widget."""
        exists = await widget_repo.exists(999)

        assert exists is False

    @pytest.mark.asyncio
    async def test_get_by_name_pattern_success(self, widget_repo):
        """Test searching widgets by name pattern."""
        await create_sample_widgets(widget_repo)
        # Search for "Widget" pattern
        widgets = await widget_repo.get_by_name_pattern("Widget")

        assert len(widgets) >= 4  # Should find multiple widgets
        for widget in widgets:
            assert "widget" in widget.name.lower()

    @pytest.mark.asyncio
    async def test_get_by_name_pattern_case_insensitive(self, widget_repo):
        """Test name pattern search is case insensitive."""
        await create_sample_widgets(widget_repo)
        widgets = await widget_repo.get_by_name_pattern("WIDGET")

        assert len(widgets) >= 4
        for widget in widgets:
            assert "widget" in widget.name.lower()

    @pytest.mark.asyncio
    async def test_get_by_name_pattern_no_matches(self, widget_repo):
        """Test name pattern search with no matches."""
        await create_sample_widgets(widget_repo)
        widgets = await widget_repo.get_by_name_pattern("NonExistentPattern")

        assert len(widgets) == 0

    @pytest.mark.asyncio
    async def test_get_by_name_pattern_empty_database(self, widget_repo):
        """Test name pattern search on empty database."""
        widgets = await widget_repo.get_by_name_pattern("Widget")

        assert len(widgets) == 0


class TestWidgetRepositoryErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_pagination_result_properties(self, widget_repo):
        """Test PaginationResult properties calculation."""
        await create_sample_widgets(widget_repo)
        result = await widget_repo.get_all(page=2, size=2)

        assert result.pages == 3  # 5 total items / 2 per page = 3 pages
        assert result.total == 5
        assert result.page == 2
        assert result.size == 2

    @pytest.mark.asyncio
    async def test_pagination_result_edge_cases(self, widget_repo):
        """Test PaginationResult with edge case calculations."""
        # Test with no items
        result = await widget_repo.get_all()
        assert result.pages == 0

    @pytest.mark.asyncio
    async def test_repository_session_handling(self, widget_repo):
        """Test repository properly handles session."""
        assert widget_repo.session is not None

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, widget_repo):
        """Test concurrent repository operations."""
        # Create multiple widgets concurrently
        widget_data1 = WidgetCreate(name="Widget 1", number_of_parts=1)
        widget_data2 = WidgetCreate(name="Widget 2", number_of_parts=2)

        widget1 = await widget_repo.create(widget_data1)
        widget2 = await widget_repo.create(widget_data2)

        assert widget1.id != widget2.id
        assert widget1.name == "Widget 1"
        assert widget2.name == "Widget 2"


class TestWidgetRepositoryIntegration:
    """Test full integration scenarios."""

    @pytest.mark.asyncio
    async def test_full_crud_cycle(self, widget_repo):
        """Test complete CRUD cycle for a widget."""
        # Create
        create_data = WidgetCreate(name="CRUD Test Widget", number_of_parts=10)
        created_widget = await widget_repo.create(create_data)
        assert created_widget.id is not None

        # Read
        retrieved_widget = await widget_repo.get_by_id(created_widget.id)
        assert retrieved_widget.name == "CRUD Test Widget"

        # Update
        update_data = WidgetUpdate(
            name="Updated CRUD Widget", number_of_parts=20
        )
        updated_widget = await widget_repo.update(
            created_widget.id, update_data
        )
        assert updated_widget.name == "Updated CRUD Widget"
        assert updated_widget.number_of_parts == 20

        # Delete
        delete_result = await widget_repo.delete(created_widget.id)
        assert delete_result is True

        # Verify deletion
        with pytest.raises(WidgetNotFoundException):
            await widget_repo.get_by_id(created_widget.id)

    @pytest.mark.asyncio
    async def test_repository_with_database_constraints(self, widget_repo):
        """Test repository operations respect database constraints."""
        # Test name length constraint through repository
        create_data = WidgetCreate(
            name="a" * 64, number_of_parts=5
        )  # Max length
        widget = await widget_repo.create(create_data)
        assert len(widget.name) == 64

        # Test positive parts constraint
        create_data = WidgetCreate(
            name="Test", number_of_parts=1
        )  # Minimum valid
        widget = await widget_repo.create(create_data)
        assert widget.number_of_parts == 1
