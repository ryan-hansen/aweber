"""
Pydantic schemas for Widget API request/response validation.

This module defines the Pydantic models used for validating API requests
and serializing responses for the Widget resource.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WidgetBase(BaseModel):
    """Base schema for Widget with common fields."""

    name: str = Field(
        ...,
        description="Name of the widget",
        max_length=64,
        min_length=1,
    )
    number_of_parts: int = Field(
        ...,
        description="Number of parts in the widget",
        gt=0,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        if len(v) > 64:
            raise ValueError("Name cannot exceed 64 characters")
        return v.strip()

    @field_validator("number_of_parts")
    @classmethod
    def validate_number_of_parts(cls, v: int) -> int:
        """Validate number_of_parts field."""
        if v <= 0:
            raise ValueError("Number of parts must be a positive integer")
        return v


class WidgetCreate(WidgetBase):
    """Schema for creating a new widget."""

    pass


class WidgetUpdate(BaseModel):
    """Schema for updating an existing widget (all fields optional)."""

    name: Optional[str] = Field(
        None,
        description="Name of the widget",
        max_length=64,
        min_length=1,
    )
    number_of_parts: Optional[int] = Field(
        None,
        description="Number of parts in the widget",
        gt=0,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name field."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Name cannot be empty or whitespace only")
            if len(v) > 64:
                raise ValueError("Name cannot exceed 64 characters")
            return v.strip()
        return v

    @field_validator("number_of_parts")
    @classmethod
    def validate_number_of_parts(cls, v: Optional[int]) -> Optional[int]:
        """Validate number_of_parts field."""
        if v is not None and v <= 0:
            raise ValueError("Number of parts must be a positive integer")
        return v


class WidgetResponse(WidgetBase):
    """Schema for widget API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique identifier for the widget")
    created_at: datetime = Field(
        ..., description="Timestamp when the widget was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the widget was last updated"
    )


class WidgetListResponse(BaseModel):
    """Schema for paginated widget list responses."""

    widgets: list[WidgetResponse] = Field(..., description="List of widgets")
    total: int = Field(..., description="Total number of widgets")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
