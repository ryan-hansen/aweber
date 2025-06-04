"""Repository layer for database operations."""

from .widget import (
    PaginationResult,
    WidgetCreateError,
    WidgetDeleteError,
    WidgetNotFoundError,
    WidgetRepository,
    WidgetRepositoryError,
    WidgetUpdateError,
)

__all__ = [
    "WidgetRepository",
    "PaginationResult",
    "WidgetRepositoryError",
    "WidgetNotFoundError",
    "WidgetCreateError",
    "WidgetUpdateError",
    "WidgetDeleteError",
]
