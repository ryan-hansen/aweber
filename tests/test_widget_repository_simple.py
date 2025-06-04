"""
Simple Widget repository tests.

This module provides basic smoke tests for Widget repository operations
to ensure the core functionality works correctly.
"""

import pytest

from src.app.database import (
    TestAsyncSessionLocal,
    create_test_tables,
    drop_test_tables,
)
from src.app.repositories.widget import (
    PaginationResult,
    WidgetNotFoundError,
    WidgetRepository,
)
from src.app.schemas.widget import WidgetCreate, WidgetUpdate


async def create_sample_widgets(repo: WidgetRepository):
    """Helper function to create sample widgets in a repository."""
    widgets = []
    sample_data = [
        WidgetCreate(name="Widget A", number_of_parts=5),
        WidgetCreate(name="Widget B", number_of_parts=10),
        WidgetCreate(name="Test Widget", number_of_parts=20),
    ]

    for widget_data in sample_data:
        widget = await repo.create(widget_data)
        widgets.append(widget)

    return widgets


class TestWidgetRepositoryCore:
    """Test core Widget repository functionality."""

    @pytest.mark.asyncio
    async def test_create_widget_success(self):
        """Test successful widget creation."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)
            widget_data = WidgetCreate(name="Test Widget", number_of_parts=5)

            widget = await widget_repo.create(widget_data)

            assert widget.id is not None
            assert widget.name == "Test Widget"
            assert widget.number_of_parts == 5
            assert widget.created_at is not None
            assert widget.updated_at is not None

    @pytest.mark.asyncio
    async def test_get_by_id_success(self):
        """Test successful widget retrieval by ID."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)
            sample_widgets = await create_sample_widgets(widget_repo)
            widget_id = sample_widgets[0].id

            widget = await widget_repo.get_by_id(widget_id)

            assert widget.id == widget_id
            assert widget.name == sample_widgets[0].name
            assert widget.number_of_parts == sample_widgets[0].number_of_parts

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test widget retrieval with non-existent ID."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)

            with pytest.raises(WidgetNotFoundError) as exc_info:
                await widget_repo.get_by_id(999)

            assert "Widget with ID 999 not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self):
        """Test getting all widgets with pagination."""
        await drop_test_tables()  # Clean slate
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)
            await create_sample_widgets(widget_repo)

            result = await widget_repo.get_all()

            assert isinstance(result, PaginationResult)
            assert len(result.items) == 3
            assert result.total == 3
            assert result.page == 1
            assert result.size == 10
            assert result.pages == 1

    @pytest.mark.asyncio
    async def test_update_widget_success(self):
        """Test successful widget update."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)
            sample_widgets = await create_sample_widgets(widget_repo)
            widget_id = sample_widgets[0].id

            update_data = WidgetUpdate(
                name="Updated Widget", number_of_parts=100
            )
            updated_widget = await widget_repo.update(widget_id, update_data)

            assert updated_widget.id == widget_id
            assert updated_widget.name == "Updated Widget"
            assert updated_widget.number_of_parts == 100

    @pytest.mark.asyncio
    async def test_update_widget_not_found(self):
        """Test updating non-existent widget."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)
            update_data = WidgetUpdate(name="Updated Widget")

            with pytest.raises(WidgetNotFoundError):
                await widget_repo.update(999, update_data)

    @pytest.mark.asyncio
    async def test_delete_widget_success(self):
        """Test successful widget deletion."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)
            sample_widgets = await create_sample_widgets(widget_repo)
            widget_id = sample_widgets[0].id

            result = await widget_repo.delete(widget_id)

            assert result is True

            # Verify widget is deleted
            with pytest.raises(WidgetNotFoundError):
                await widget_repo.get_by_id(widget_id)

    @pytest.mark.asyncio
    async def test_delete_widget_not_found(self):
        """Test deleting non-existent widget."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)

            with pytest.raises(WidgetNotFoundError):
                await widget_repo.delete(999)

    @pytest.mark.asyncio
    async def test_exists_widget(self):
        """Test widget existence check."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)
            sample_widgets = await create_sample_widgets(widget_repo)
            widget_id = sample_widgets[0].id

            # Test existing widget
            exists = await widget_repo.exists(widget_id)
            assert exists is True

            # Test non-existent widget
            exists = await widget_repo.exists(999)
            assert exists is False

    @pytest.mark.asyncio
    async def test_get_by_name_pattern(self):
        """Test searching widgets by name pattern."""
        await drop_test_tables()  # Clean slate
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)
            await create_sample_widgets(widget_repo)

            # Search for "Widget" pattern
            widgets = await widget_repo.get_by_name_pattern("Widget")

            assert len(widgets) == 3  # Should find exactly 3 widgets
            for widget in widgets:
                assert "widget" in widget.name.lower()

    @pytest.mark.asyncio
    async def test_pydantic_validation_errors(self):
        """Test that Pydantic validation prevents invalid data."""
        # Test invalid name (empty)
        with pytest.raises(ValueError):
            WidgetCreate(name="", number_of_parts=5)

        # Test invalid number_of_parts (zero)
        with pytest.raises(ValueError):
            WidgetCreate(name="Test", number_of_parts=0)

        # Test invalid number_of_parts (negative)
        with pytest.raises(ValueError):
            WidgetCreate(name="Test", number_of_parts=-1)

        # Test invalid name (too long)
        with pytest.raises(ValueError):
            WidgetCreate(name="a" * 65, number_of_parts=5)

    @pytest.mark.asyncio
    async def test_full_crud_cycle(self):
        """Test complete CRUD cycle for a widget."""
        await create_test_tables()

        async with TestAsyncSessionLocal() as session:
            widget_repo = WidgetRepository(session)

            # Create
            widget_data = WidgetCreate(
                name="CRUD Test Widget", number_of_parts=42
            )
            created_widget = await widget_repo.create(widget_data)
            assert created_widget.id is not None

            # Read
            retrieved_widget = await widget_repo.get_by_id(created_widget.id)
            assert retrieved_widget.name == "CRUD Test Widget"
            assert retrieved_widget.number_of_parts == 42

            # Update
            update_data = WidgetUpdate(
                name="Updated CRUD Widget", number_of_parts=84
            )
            updated_widget = await widget_repo.update(
                created_widget.id, update_data
            )
            assert updated_widget.name == "Updated CRUD Widget"
            assert updated_widget.number_of_parts == 84

            # Delete
            delete_result = await widget_repo.delete(created_widget.id)
            assert delete_result is True

            # Verify deletion
            with pytest.raises(WidgetNotFoundError):
                await widget_repo.get_by_id(created_widget.id)
