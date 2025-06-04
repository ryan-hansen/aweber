"""
Tests for Widget Pydantic schemas.

This module tests all Widget schemas for proper validation, serialization,
and error handling.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.app.models.widget import Widget
from src.app.schemas.widget import (
    WidgetBase,
    WidgetCreate,
    WidgetListResponse,
    WidgetResponse,
    WidgetUpdate,
)


class TestWidgetBase:
    """Test the WidgetBase schema."""

    def test_valid_widget_base(self):
        """Test creating a valid WidgetBase."""
        data = {"name": "Test Widget", "number_of_parts": 5}
        widget = WidgetBase(**data)
        assert widget.name == "Test Widget"
        assert widget.number_of_parts == 5

    def test_name_validation_max_length(self):
        """Test name validation with maximum length."""
        # 64 characters should be valid
        valid_name = "a" * 64
        widget = WidgetBase(name=valid_name, number_of_parts=1)
        assert widget.name == valid_name

        # 65 characters should fail
        invalid_name = "a" * 65
        with pytest.raises(ValidationError) as exc_info:
            WidgetBase(name=invalid_name, number_of_parts=1)
        assert "String should have at most 64 characters" in str(
            exc_info.value
        )

    def test_name_validation_empty(self):
        """Test name validation with empty values."""
        # Empty string should fail
        with pytest.raises(ValidationError) as exc_info:
            WidgetBase(name="", number_of_parts=1)
        assert "String should have at least 1 character" in str(exc_info.value)

        # Whitespace only should fail
        with pytest.raises(ValidationError) as exc_info:
            WidgetBase(name="   ", number_of_parts=1)
        assert "Name cannot be empty or whitespace only" in str(exc_info.value)

    def test_name_validation_whitespace_trim(self):
        """Test name validation trims whitespace."""
        widget = WidgetBase(name="  Test Widget  ", number_of_parts=1)
        assert widget.name == "Test Widget"

    def test_number_of_parts_validation_positive(self):
        """Test number_of_parts validation with positive integers."""
        # Positive integers should be valid
        widget = WidgetBase(name="Test", number_of_parts=1)
        assert widget.number_of_parts == 1

        widget = WidgetBase(name="Test", number_of_parts=100)
        assert widget.number_of_parts == 100

    def test_number_of_parts_validation_invalid(self):
        """Test number_of_parts validation with invalid values."""
        # Zero should fail
        with pytest.raises(ValidationError) as exc_info:
            WidgetBase(name="Test", number_of_parts=0)
        assert "Input should be greater than 0" in str(exc_info.value)

        # Negative should fail
        with pytest.raises(ValidationError) as exc_info:
            WidgetBase(name="Test", number_of_parts=-1)
        assert "Input should be greater than 0" in str(exc_info.value)

    def test_required_fields(self):
        """Test that required fields are enforced."""
        # Missing name
        with pytest.raises(ValidationError) as exc_info:
            WidgetBase(number_of_parts=1)
        assert "Field required" in str(exc_info.value)

        # Missing number_of_parts
        with pytest.raises(ValidationError) as exc_info:
            WidgetBase(name="Test")
        assert "Field required" in str(exc_info.value)


class TestWidgetCreate:
    """Test the WidgetCreate schema."""

    def test_valid_widget_create(self):
        """Test creating a valid WidgetCreate."""
        data = {"name": "New Widget", "number_of_parts": 10}
        widget = WidgetCreate(**data)
        assert widget.name == "New Widget"
        assert widget.number_of_parts == 10

    def test_inherits_validation_from_base(self):
        """Test that WidgetCreate inherits validation from WidgetBase."""
        # Should fail with invalid name
        with pytest.raises(ValidationError):
            WidgetCreate(name="", number_of_parts=1)

        # Should fail with invalid number_of_parts
        with pytest.raises(ValidationError):
            WidgetCreate(name="Test", number_of_parts=0)


class TestWidgetUpdate:
    """Test the WidgetUpdate schema."""

    def test_valid_widget_update_all_fields(self):
        """Test updating all fields."""
        data = {"name": "Updated Widget", "number_of_parts": 15}
        widget = WidgetUpdate(**data)
        assert widget.name == "Updated Widget"
        assert widget.number_of_parts == 15

    def test_valid_widget_update_partial(self):
        """Test partial updates with optional fields."""
        # Only name
        widget = WidgetUpdate(name="Updated Name")
        assert widget.name == "Updated Name"
        assert widget.number_of_parts is None

        # Only number_of_parts
        widget = WidgetUpdate(number_of_parts=20)
        assert widget.name is None
        assert widget.number_of_parts == 20

        # Empty update (all fields None)
        widget = WidgetUpdate()
        assert widget.name is None
        assert widget.number_of_parts is None

    def test_name_validation_when_provided(self):
        """Test name validation when provided in update."""
        # Valid name should work
        widget = WidgetUpdate(name="Valid Name")
        assert widget.name == "Valid Name"

        # Invalid name should fail
        with pytest.raises(ValidationError) as exc_info:
            WidgetUpdate(name="")
        assert "String should have at least 1 character" in str(exc_info.value)

        # Long name should fail
        with pytest.raises(ValidationError) as exc_info:
            WidgetUpdate(name="a" * 65)
        assert "String should have at most 64 characters" in str(
            exc_info.value
        )

    def test_number_of_parts_validation_when_provided(self):
        """Test number_of_parts validation when provided in update."""
        # Valid number should work
        widget = WidgetUpdate(number_of_parts=5)
        assert widget.number_of_parts == 5

        # Invalid number should fail
        with pytest.raises(ValidationError) as exc_info:
            WidgetUpdate(number_of_parts=0)
        assert "Input should be greater than 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            WidgetUpdate(number_of_parts=-1)
        assert "Input should be greater than 0" in str(exc_info.value)

    def test_whitespace_trimming_in_update(self):
        """Test whitespace trimming in update schema."""
        widget = WidgetUpdate(name="  Trimmed Name  ")
        assert widget.name == "Trimmed Name"


class TestWidgetResponse:
    """Test the WidgetResponse schema."""

    def test_valid_widget_response(self):
        """Test creating a valid WidgetResponse."""
        now = datetime.now()
        data = {
            "id": 1,
            "name": "Response Widget",
            "number_of_parts": 8,
            "created_at": now,
            "updated_at": now,
        }
        widget = WidgetResponse(**data)
        assert widget.id == 1
        assert widget.name == "Response Widget"
        assert widget.number_of_parts == 8
        assert widget.created_at == now
        assert widget.updated_at == now

    def test_from_orm_model(self):
        """Test creating WidgetResponse from ORM model."""
        # Create a mock Widget model (without saving to DB)
        now = datetime.now()
        widget_orm = Widget(
            id=1,
            name="ORM Widget",
            number_of_parts=12,
            created_at=now,
            updated_at=now,
        )

        # Convert to Pydantic model
        widget_response = WidgetResponse.model_validate(widget_orm)
        assert widget_response.id == 1
        assert widget_response.name == "ORM Widget"
        assert widget_response.number_of_parts == 12
        assert widget_response.created_at == now
        assert widget_response.updated_at == now

    def test_datetime_serialization(self):
        """Test datetime serialization format."""
        now = datetime.now()
        widget = WidgetResponse(
            id=1,
            name="DateTime Test",
            number_of_parts=5,
            created_at=now,
            updated_at=now,
        )

        # Convert to dict and check datetime format
        widget_dict = widget.model_dump()
        assert isinstance(widget_dict["created_at"], datetime)
        assert isinstance(widget_dict["updated_at"], datetime)

        # Convert to JSON and check ISO format
        widget_json = widget.model_dump_json()
        assert now.isoformat() in widget_json


class TestWidgetListResponse:
    """Test the WidgetListResponse schema."""

    def test_valid_widget_list_response(self):
        """Test creating a valid WidgetListResponse."""
        now = datetime.now()
        widgets = [
            WidgetResponse(
                id=1,
                name="Widget 1",
                number_of_parts=5,
                created_at=now,
                updated_at=now,
            ),
            WidgetResponse(
                id=2,
                name="Widget 2",
                number_of_parts=10,
                created_at=now,
                updated_at=now,
            ),
        ]

        list_response = WidgetListResponse(
            widgets=widgets, total=2, page=1, size=10, pages=1
        )

        assert len(list_response.widgets) == 2
        assert list_response.total == 2
        assert list_response.page == 1
        assert list_response.size == 10
        assert list_response.pages == 1

    def test_empty_widget_list_response(self):
        """Test empty widget list response."""
        list_response = WidgetListResponse(
            widgets=[], total=0, page=1, size=10, pages=0
        )

        assert len(list_response.widgets) == 0
        assert list_response.total == 0
        assert list_response.page == 1
        assert list_response.size == 10
        assert list_response.pages == 0

    def test_pagination_fields(self):
        """Test pagination field validation."""
        # All fields are required
        with pytest.raises(ValidationError):
            WidgetListResponse(widgets=[])  # Missing required fields


class TestSchemaIntegration:
    """Test schema integration and edge cases."""

    def test_json_serialization_full_cycle(self):
        """Test full JSON serialization/deserialization cycle."""
        now = datetime.now()

        # Create response
        widget_response = WidgetResponse(
            id=1,
            name="JSON Test",
            number_of_parts=7,
            created_at=now,
            updated_at=now,
        )

        # Serialize to JSON
        json_str = widget_response.model_dump_json()

        # Parse back from JSON
        data = widget_response.model_validate_json(json_str)
        assert data.id == 1
        assert data.name == "JSON Test"
        assert data.number_of_parts == 7

    def test_field_descriptions_present(self):
        """Test that field descriptions are present for API documentation."""
        # Check WidgetBase fields have descriptions
        schema = WidgetBase.model_json_schema()
        assert "description" in schema["properties"]["name"]
        assert "description" in schema["properties"]["number_of_parts"]

        # Check WidgetResponse fields have descriptions
        schema = WidgetResponse.model_json_schema()
        assert "description" in schema["properties"]["id"]
        assert "description" in schema["properties"]["created_at"]
        assert "description" in schema["properties"]["updated_at"]
