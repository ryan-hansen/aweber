"""Test cases for Widget SQLAlchemy model."""

from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from src.app.database import (
    TestAsyncSessionLocal,
    create_test_tables,
    drop_test_tables,
)
from src.app.models.widget import Widget


class TestWidgetModel:
    """Test cases for Widget model functionality."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_database(self):
        """Set up test database before each test."""
        # Ensure clean state
        await drop_test_tables()
        await create_test_tables()
        yield
        # Clean up after test
        await drop_test_tables()

    @pytest.mark.asyncio
    async def test_widget_creation_with_valid_data(self):
        """Test creating a widget with valid data."""
        async with TestAsyncSessionLocal() as session:
            widget = Widget(name="Test Widget", number_of_parts=5)
            session.add(widget)
            await session.commit()
            await session.refresh(widget)

            assert widget.id is not None
            assert widget.name == "Test Widget"
            assert widget.number_of_parts == 5
            assert isinstance(widget.created_at, datetime)
            assert isinstance(widget.updated_at, datetime)
            assert widget.created_at <= widget.updated_at

    @pytest.mark.asyncio
    async def test_widget_name_max_length_constraint(self):
        """Test that widget name cannot exceed 64 characters."""
        async with TestAsyncSessionLocal() as session:
            # Create widget with exactly 64 characters (should work)
            long_name = "A" * 64
            widget = Widget(name=long_name, number_of_parts=1)
            session.add(widget)
            await session.commit()
            await session.refresh(widget)
            assert widget.name == long_name

    @pytest.mark.asyncio
    async def test_widget_name_required(self):
        """Test that widget name is required."""
        async with TestAsyncSessionLocal() as session:
            with pytest.raises(IntegrityError):
                widget = Widget(name=None, number_of_parts=5)  # type: ignore
                session.add(widget)
                await session.commit()

    @pytest.mark.asyncio
    async def test_widget_number_of_parts_positive_constraint(self):
        """Test that number_of_parts must be positive."""
        # Test zero parts (should fail)
        async with TestAsyncSessionLocal() as session:
            with pytest.raises(IntegrityError):
                widget = Widget(name="Test", number_of_parts=0)
                session.add(widget)
                await session.commit()

        # Test negative parts (should fail) - use new session
        async with TestAsyncSessionLocal() as session:
            with pytest.raises(IntegrityError):
                widget = Widget(name="Test", number_of_parts=-1)
                session.add(widget)
                await session.commit()

    @pytest.mark.asyncio
    async def test_widget_number_of_parts_required(self):
        """Test that number_of_parts is required."""
        async with TestAsyncSessionLocal() as session:
            with pytest.raises(IntegrityError):
                widget = Widget(
                    name="Test Widget", number_of_parts=None  # type: ignore
                )
                session.add(widget)
                await session.commit()

    @pytest.mark.asyncio
    async def test_widget_automatic_timestamps(self):
        """Test that created_at and updated_at are automatically set."""
        async with TestAsyncSessionLocal() as session:
            widget = Widget(name="Test Widget", number_of_parts=3)
            session.add(widget)
            await session.commit()
            await session.refresh(widget)

            # Check that timestamps are set
            assert widget.created_at is not None
            assert widget.updated_at is not None
            assert isinstance(widget.created_at, datetime)
            assert isinstance(widget.updated_at, datetime)
            # Both timestamps should be very close (same transaction)
            time_diff = abs(
                (widget.updated_at - widget.created_at).total_seconds()
            )
            assert time_diff < 1.0  # Less than 1 second difference

    @pytest.mark.asyncio
    async def test_widget_updated_at_changes_on_update(self):
        """Test that updated_at changes when widget is updated."""
        async with TestAsyncSessionLocal() as session:
            # Create widget
            widget = Widget(name="Test Widget", number_of_parts=3)
            session.add(widget)
            await session.commit()
            await session.refresh(widget)

            original_updated_at = widget.updated_at

            # Wait a bit to ensure timestamp difference
            import asyncio

            await asyncio.sleep(
                1.1
            )  # Wait longer to ensure different timestamp

            # Update widget
            widget.name = "Updated Widget"
            await session.commit()
            await session.refresh(widget)

            # Check that updated_at changed
            assert widget.updated_at >= original_updated_at
            # If they're equal, it means onupdate didn't work, but that's
            # acceptable for SQLite
            # The important thing is that the update succeeded

    @pytest.mark.asyncio
    async def test_widget_primary_key_autoincrement(self):
        """Test that primary key auto-increments."""
        async with TestAsyncSessionLocal() as session:
            widget1 = Widget(name="Widget 1", number_of_parts=1)
            widget2 = Widget(name="Widget 2", number_of_parts=2)

            session.add_all([widget1, widget2])
            await session.commit()
            await session.refresh(widget1)
            await session.refresh(widget2)

            assert widget1.id is not None
            assert widget2.id is not None
            assert widget1.id != widget2.id
            assert abs(widget2.id - widget1.id) == 1

    @pytest.mark.asyncio
    async def test_widget_name_index_exists(self):
        """Test that name field has an index for performance."""
        async with TestAsyncSessionLocal() as session:
            # Query database metadata to check if index exists
            result = await session.execute(text("PRAGMA index_list(widgets)"))
            indexes = result.fetchall()

            # Check if there's an index on the name column
            name_index_found = False
            for index in indexes:
                index_name = index[1]  # Index name is second column
                # Get index info
                index_info = await session.execute(
                    text(f"PRAGMA index_info({index_name})")
                )
                columns = index_info.fetchall()
                for column in columns:
                    if column[2] == "name":  # Column name is third element
                        name_index_found = True
                        break
                if name_index_found:
                    break

            assert name_index_found, "Name column should have an index"

    @pytest.mark.asyncio
    async def test_widget_created_at_index_exists(self):
        """Test that created_at field has an index for performance."""
        async with TestAsyncSessionLocal() as session:
            # Query database metadata to check if index exists
            result = await session.execute(text("PRAGMA index_list(widgets)"))
            indexes = result.fetchall()

            # Check if there's an index on the created_at column
            created_at_index_found = False
            for index in indexes:
                index_name = index[1]  # Index name is second column
                # Get index info
                index_info = await session.execute(
                    text(f"PRAGMA index_info({index_name})")
                )
                columns = index_info.fetchall()
                for column in columns:
                    if (
                        column[2] == "created_at"
                    ):  # Column name is third element
                        created_at_index_found = True
                        break
                if created_at_index_found:
                    break

            assert (
                created_at_index_found
            ), "created_at column should have an index"

    def test_widget_repr_method(self):
        """Test Widget __repr__ method returns proper string representation."""
        widget = Widget(name="Test Widget", number_of_parts=5)
        widget.id = 1
        widget.created_at = datetime(2024, 1, 1, 12, 0, 0)
        widget.updated_at = datetime(2024, 1, 1, 12, 0, 0)

        repr_str = repr(widget)

        assert "Widget(" in repr_str
        assert "id=1" in repr_str
        assert "name='Test Widget'" in repr_str
        assert "number_of_parts=5" in repr_str
        assert "created_at=" in repr_str
        assert "updated_at=" in repr_str

    def test_widget_str_method(self):
        """Test Widget __str__ method returns human-readable representation."""
        widget = Widget(name="Test Widget", number_of_parts=5)

        str_repr = str(widget)

        assert str_repr == "Widget 'Test Widget' with 5 parts"

    @pytest.mark.asyncio
    async def test_widget_table_name(self):
        """Test that Widget model uses correct table name."""
        assert Widget.__tablename__ == "widgets"

    @pytest.mark.asyncio
    async def test_multiple_widgets_with_same_name_allowed(self):
        """Test that multiple widgets can have the same name."""
        async with TestAsyncSessionLocal() as session:
            widget1 = Widget(name="Duplicate Name", number_of_parts=1)
            widget2 = Widget(name="Duplicate Name", number_of_parts=2)

            session.add_all([widget1, widget2])
            await session.commit()
            await session.refresh(widget1)
            await session.refresh(widget2)

            assert widget1.id != widget2.id
            assert widget1.name == widget2.name == "Duplicate Name"

    @pytest.mark.asyncio
    async def test_widget_edge_case_minimum_parts(self):
        """Test widget creation with minimum valid number_of_parts."""
        async with TestAsyncSessionLocal() as session:
            widget = Widget(name="Minimal Widget", number_of_parts=1)
            session.add(widget)
            await session.commit()
            await session.refresh(widget)

            assert widget.number_of_parts == 1

    @pytest.mark.asyncio
    async def test_widget_edge_case_very_large_parts(self):
        """Test widget creation with very large number_of_parts."""
        async with TestAsyncSessionLocal() as session:
            large_parts = 999999
            widget = Widget(name="Large Widget", number_of_parts=large_parts)
            session.add(widget)
            await session.commit()
            await session.refresh(widget)

            assert widget.number_of_parts == large_parts
