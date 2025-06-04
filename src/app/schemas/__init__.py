"""Pydantic schemas for API validation."""

from .widget import (
    WidgetBase,
    WidgetCreate,
    WidgetListResponse,
    WidgetResponse,
    WidgetUpdate,
)

__all__ = [
    "WidgetBase",
    "WidgetCreate",
    "WidgetUpdate",
    "WidgetResponse",
    "WidgetListResponse",
]
