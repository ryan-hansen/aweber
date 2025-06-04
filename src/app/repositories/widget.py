"""
Widget repository for database operations.

This module implements the repository pattern for Widget CRUD operations
with proper error handling, pagination, and async SQLAlchemy 2.0 support.
"""

import logging
from typing import Sequence

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.widget import Widget
from ..schemas.widget import WidgetCreate, WidgetUpdate

logger = logging.getLogger(__name__)


class WidgetRepositoryError(Exception):
    """Base exception for widget repository operations."""

    pass


class WidgetNotFoundError(WidgetRepositoryError):
    """Raised when a widget is not found."""

    pass


class WidgetCreateError(WidgetRepositoryError):
    """Raised when widget creation fails."""

    pass


class WidgetUpdateError(WidgetRepositoryError):
    """Raised when widget update fails."""

    pass


class WidgetDeleteError(WidgetRepositoryError):
    """Raised when widget deletion fails."""

    pass


class PaginationResult:
    """Container for paginated results."""

    def __init__(
        self,
        items: Sequence[Widget],
        total: int,
        page: int,
        size: int,
    ):
        self.items = items
        self.total = total
        self.page = page
        self.size = size
        self.pages = (total + size - 1) // size if size > 0 else 0


class WidgetRepository:
    """Repository for Widget database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create(self, widget_data: WidgetCreate) -> Widget:
        """
        Create a new widget.

        Args:
            widget_data: Pydantic model with widget creation data

        Returns:
            Created Widget instance

        Raises:
            WidgetCreateError: If creation fails
        """
        try:
            widget = Widget(
                name=widget_data.name,
                number_of_parts=widget_data.number_of_parts,
            )
            self.session.add(widget)
            await self.session.commit()
            await self.session.refresh(widget)

            logger.info(f"Created widget with ID {widget.id}")
            return widget

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Integrity error creating widget: {e}")
            raise WidgetCreateError(
                f"Failed to create widget: {str(e)}"
            ) from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error creating widget: {e}")
            raise WidgetCreateError(
                f"Database error creating widget: {str(e)}"
            ) from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error creating widget: {e}")
            raise WidgetCreateError(
                f"Unexpected error creating widget: {str(e)}"
            ) from e

    async def get_by_id(self, widget_id: int) -> Widget:
        """
        Get a widget by ID.

        Args:
            widget_id: Widget ID to retrieve

        Returns:
            Widget instance

        Raises:
            WidgetNotFoundError: If widget is not found
        """
        try:
            stmt = select(Widget).where(Widget.id == widget_id)
            result = await self.session.execute(stmt)
            widget = result.scalar_one_or_none()

            if widget is None:
                raise WidgetNotFoundError(
                    f"Widget with ID {widget_id} not found"
                )

            logger.debug(f"Retrieved widget with ID {widget_id}")
            return widget

        except WidgetNotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving widget {widget_id}: {e}")
            raise WidgetRepositoryError(
                f"Database error retrieving widget: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error retrieving widget {widget_id}: {e}"
            )
            raise WidgetRepositoryError(
                f"Unexpected error retrieving widget: {str(e)}"
            ) from e

    async def get_all(
        self,
        page: int = 1,
        size: int = 10,
        order_by: str = "id",
        order_desc: bool = False,
    ) -> PaginationResult:
        """
        Get all widgets with pagination.

        Args:
            page: Page number (1-based)
            size: Number of items per page
            order_by: Field to order by (id, name, created_at, updated_at)
            order_desc: Whether to order in descending order

        Returns:
            PaginationResult with widgets and pagination info

        Raises:
            WidgetRepositoryError: If query fails
        """
        try:
            # Validate pagination parameters
            if page < 1:
                page = 1
            if size < 1:
                size = 10
            if size > 100:  # Limit max page size
                size = 100

            # Calculate offset
            offset = (page - 1) * size

            # Validate order_by field
            valid_order_fields = {"id", "name", "created_at", "updated_at"}
            if order_by not in valid_order_fields:
                order_by = "id"

            # Get order column
            order_column = getattr(Widget, order_by)
            if order_desc:
                order_column = order_column.desc()

            # Get total count
            count_stmt = select(func.count(Widget.id))
            total_result = await self.session.execute(count_stmt)
            total = total_result.scalar_one()

            # Get paginated results
            stmt = (
                select(Widget)
                .order_by(order_column)
                .offset(offset)
                .limit(size)
            )
            result = await self.session.execute(stmt)
            widgets = result.scalars().all()

            logger.debug(
                f"Retrieved {len(widgets)} widgets "
                f"(page {page}, size {size}, total {total})"
            )

            return PaginationResult(
                items=widgets,
                total=total,
                page=page,
                size=size,
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving widgets: {e}")
            raise WidgetRepositoryError(
                f"Database error retrieving widgets: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error retrieving widgets: {e}")
            raise WidgetRepositoryError(
                f"Unexpected error retrieving widgets: {str(e)}"
            ) from e

    async def update(
        self, widget_id: int, widget_data: WidgetUpdate
    ) -> Widget:
        """
        Update a widget.

        Args:
            widget_id: Widget ID to update
            widget_data: Pydantic model with update data

        Returns:
            Updated Widget instance

        Raises:
            WidgetNotFoundError: If widget is not found
            WidgetUpdateError: If update fails
        """
        try:
            # First check if widget exists
            widget = await self.get_by_id(widget_id)

            # Prepare update data (only include non-None fields)
            update_data = widget_data.model_dump(exclude_unset=True)
            if not update_data:
                # No fields to update, return existing widget
                return widget

            # Update the widget
            stmt = (
                update(Widget)
                .where(Widget.id == widget_id)
                .values(**update_data)
                .returning(Widget)
            )
            result = await self.session.execute(stmt)
            updated_widget = result.scalar_one()

            await self.session.commit()
            await self.session.refresh(updated_widget)

            logger.info(f"Updated widget with ID {widget_id}")
            return updated_widget

        except WidgetNotFoundError:
            raise
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Integrity error updating widget {widget_id}: {e}")
            raise WidgetUpdateError(
                f"Failed to update widget: {str(e)}"
            ) from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error updating widget {widget_id}: {e}")
            raise WidgetUpdateError(
                f"Database error updating widget: {str(e)}"
            ) from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error updating widget {widget_id}: {e}")
            raise WidgetUpdateError(
                f"Unexpected error updating widget: {str(e)}"
            ) from e

    async def delete(self, widget_id: int) -> bool:
        """
        Delete a widget.

        Args:
            widget_id: Widget ID to delete

        Returns:
            True if deleted successfully

        Raises:
            WidgetNotFoundError: If widget is not found
            WidgetDeleteError: If deletion fails
        """
        try:
            # First check if widget exists
            await self.get_by_id(widget_id)

            # Delete the widget
            stmt = delete(Widget).where(Widget.id == widget_id)
            result = await self.session.execute(stmt)

            if result.rowcount == 0:
                raise WidgetNotFoundError(
                    f"Widget with ID {widget_id} not found"
                )

            await self.session.commit()
            logger.info(f"Deleted widget with ID {widget_id}")
            return True

        except WidgetNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error deleting widget {widget_id}: {e}")
            raise WidgetDeleteError(
                f"Database error deleting widget: {str(e)}"
            ) from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error deleting widget {widget_id}: {e}")
            raise WidgetDeleteError(
                f"Unexpected error deleting widget: {str(e)}"
            ) from e

    async def exists(self, widget_id: int) -> bool:
        """
        Check if a widget exists.

        Args:
            widget_id: Widget ID to check

        Returns:
            True if widget exists, False otherwise
        """
        try:
            stmt = select(func.count(Widget.id)).where(Widget.id == widget_id)
            result = await self.session.execute(stmt)
            count = result.scalar_one()
            return count > 0

        except SQLAlchemyError as e:
            logger.error(
                f"Database error checking widget existence {widget_id}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error checking widget existence {widget_id}: {e}"
            )
            return False

    async def get_by_name_pattern(self, name_pattern: str) -> Sequence[Widget]:
        """
        Get widgets by name pattern (case-insensitive).

        Args:
            name_pattern: Pattern to search for in widget names

        Returns:
            List of matching widgets

        Raises:
            WidgetRepositoryError: If query fails
        """
        try:
            stmt = (
                select(Widget)
                .where(Widget.name.ilike(f"%{name_pattern}%"))
                .order_by(Widget.name)
            )

            result = await self.session.execute(stmt)
            widgets = result.scalars().all()

            logger.debug(
                f"Found {len(widgets)} widgets matching "
                f"pattern '{name_pattern}'"
            )
            return widgets

        except SQLAlchemyError as e:
            logger.error(f"Database error searching widgets: {e}")
            raise WidgetRepositoryError(
                f"Database error searching widgets: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error searching widgets: {e}")
            raise WidgetRepositoryError(
                f"Unexpected error searching widgets: {str(e)}"
            ) from e
