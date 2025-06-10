"""
Tests for Widget API endpoints.

This module tests all Widget API endpoints including CRUD operations,
error handling, validation, pagination, and OpenAPI documentation.
"""

from fastapi import status


class TestWidgetCreateEndpoint:
    """Test POST /widgets endpoint."""

    def test_create_widget_success(self, client):
        """Test successful widget creation."""
        widget_data = {
            "name": "Test Widget",
            "number_of_parts": 10,
        }

        response = client.post("/widgets/", json=widget_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Widget"
        assert data["number_of_parts"] == 10
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_widget_validation_error_empty_name(self, client):
        """Test widget creation with empty name."""
        widget_data = {
            "name": "",
            "number_of_parts": 10,
        }

        response = client.post("/widgets/", json=widget_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["error"] == "VALIDATION_ERROR"
        assert "message" in data
        assert "details" in data
        assert "field_errors" in data["details"]

    def test_create_widget_validation_error_missing_name(self, client):
        """Test widget creation with missing name."""
        widget_data = {
            "number_of_parts": 10,
        }

        response = client.post("/widgets/", json=widget_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_widget_validation_error_negative_parts(self, client):
        """Test widget creation with negative number of parts."""
        widget_data = {
            "name": "Test Widget",
            "number_of_parts": -5,
        }

        response = client.post("/widgets/", json=widget_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_widget_validation_error_zero_parts(self, client):
        """Test widget creation with zero number of parts."""
        widget_data = {
            "name": "Test Widget",
            "number_of_parts": 0,
        }

        response = client.post("/widgets/", json=widget_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_widget_validation_error_name_too_long(self, client):
        """Test widget creation with name exceeding max length."""
        widget_data = {
            "name": "x" * 65,  # Exceeds 64 character limit
            "number_of_parts": 10,
        }

        response = client.post("/widgets/", json=widget_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_widget_name_trimming(self, client):
        """Test that widget names are trimmed."""
        widget_data = {
            "name": "  Test Widget  ",
            "number_of_parts": 10,
        }

        response = client.post("/widgets/", json=widget_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Widget"  # Should be trimmed


class TestWidgetListEndpoint:
    """Test GET /widgets endpoint."""

    def test_get_widgets_empty_list(self, client):
        """Test getting widgets from empty database."""
        response = client.get("/widgets/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["widgets"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 0

    def test_get_widgets_with_data(self, client):
        """Test getting widgets with data."""
        # Create test widgets
        widgets_data = [
            {"name": "Widget A", "number_of_parts": 5},
            {"name": "Widget B", "number_of_parts": 10},
            {"name": "Widget C", "number_of_parts": 15},
        ]

        for widget_data in widgets_data:
            client.post("/widgets/", json=widget_data)

        response = client.get("/widgets/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["widgets"]) == 3
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 1

        # Verify widget structure
        widget = data["widgets"][0]
        assert "id" in widget
        assert "name" in widget
        assert "number_of_parts" in widget
        assert "created_at" in widget
        assert "updated_at" in widget

    def test_get_widgets_pagination(self, client):
        """Test widget pagination."""
        # Create 5 test widgets
        for i in range(5):
            widget_data = {"name": f"Widget {i}", "number_of_parts": i + 1}
            client.post("/widgets/", json=widget_data)

        # Get page 1 with size 2
        response = client.get("/widgets/?page=1&size=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["widgets"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["pages"] == 3

        # Get page 2 with size 2
        response = client.get("/widgets/?page=2&size=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["widgets"]) == 2
        assert data["page"] == 2

    def test_get_widgets_ordering(self, client):
        """Test widget ordering."""
        # Create test widgets
        widgets_data = [
            {"name": "Zebra Widget", "number_of_parts": 1},
            {"name": "Alpha Widget", "number_of_parts": 2},
            {"name": "Beta Widget", "number_of_parts": 3},
        ]

        for widget_data in widgets_data:
            client.post("/widgets/", json=widget_data)

        # Test ascending order by name
        response = client.get("/widgets/?order_by=name&order_desc=false")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        names = [widget["name"] for widget in data["widgets"]]
        assert names == ["Alpha Widget", "Beta Widget", "Zebra Widget"]

        # Test descending order by name
        response = client.get("/widgets/?order_by=name&order_desc=true")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        names = [widget["name"] for widget in data["widgets"]]
        assert names == ["Zebra Widget", "Beta Widget", "Alpha Widget"]

    def test_get_widgets_invalid_pagination_params(self, client):
        """Test widget list with invalid pagination parameters."""
        # Invalid page number (should default to 1)
        response = client.get("/widgets/?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid size (should be rejected)
        response = client.get("/widgets/?size=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Size too large (should be rejected)
        response = client.get("/widgets/?size=101")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestWidgetGetByIdEndpoint:
    """Test GET /widgets/{id} endpoint."""

    def test_get_widget_by_id_success(self, client):
        """Test successful widget retrieval by ID."""
        # Create a widget
        widget_data = {"name": "Test Widget", "number_of_parts": 10}
        create_response = client.post("/widgets/", json=widget_data)
        widget_id = create_response.json()["id"]

        # Get the widget by ID
        response = client.get(f"/widgets/{widget_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == widget_id
        assert data["name"] == "Test Widget"
        assert data["number_of_parts"] == 10

    def test_get_widget_by_id_not_found(self, client):
        """Test widget retrieval with non-existent ID."""
        response = client.get("/widgets/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["error"] == "WIDGET_NOT_FOUND"
        assert "message" in data
        assert "details" in data
        assert "widget_id" in data["details"]

    def test_get_widget_by_id_invalid_id(self, client):
        """Test widget retrieval with invalid ID format."""
        response = client.get("/widgets/invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestWidgetUpdateEndpoint:
    """Test PUT /widgets/{id} endpoint."""

    def test_update_widget_success(self, client):
        """Test successful widget update."""
        # Create a widget
        widget_data = {"name": "Original Widget", "number_of_parts": 5}
        create_response = client.post("/widgets/", json=widget_data)
        widget_id = create_response.json()["id"]

        # Update the widget
        update_data = {"name": "Updated Widget", "number_of_parts": 20}
        response = client.put(f"/widgets/{widget_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == widget_id
        assert data["name"] == "Updated Widget"
        assert data["number_of_parts"] == 20

    def test_update_widget_partial(self, client):
        """Test partial widget update."""
        # Create a widget
        widget_data = {"name": "Original Widget", "number_of_parts": 5}
        create_response = client.post("/widgets/", json=widget_data)
        widget_id = create_response.json()["id"]
        original_name = create_response.json()["name"]

        # Update only number_of_parts
        update_data = {"number_of_parts": 15}
        response = client.put(f"/widgets/{widget_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == original_name  # Should remain unchanged
        assert data["number_of_parts"] == 15

    def test_update_widget_not_found(self, client):
        """Test updating non-existent widget."""
        update_data = {"name": "Updated Widget"}
        response = client.put("/widgets/999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["error"] == "WIDGET_NOT_FOUND"
        assert "message" in data
        assert "details" in data
        assert "widget_id" in data["details"]

    def test_update_widget_validation_error(self, client):
        """Test widget update with invalid data."""
        # Create a widget
        widget_data = {"name": "Original Widget", "number_of_parts": 5}
        create_response = client.post("/widgets/", json=widget_data)
        widget_id = create_response.json()["id"]

        # Try to update with invalid data
        update_data = {"number_of_parts": -5}
        response = client.put(f"/widgets/{widget_id}", json=update_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_widget_empty_payload(self, client):
        """Test widget update with empty payload."""
        # Create a widget
        widget_data = {"name": "Original Widget", "number_of_parts": 5}
        create_response = client.post("/widgets/", json=widget_data)
        widget_id = create_response.json()["id"]

        # Update with empty payload (should return unchanged widget)
        response = client.put(f"/widgets/{widget_id}", json={})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Original Widget"
        assert data["number_of_parts"] == 5


class TestWidgetDeleteEndpoint:
    """Test DELETE /widgets/{id} endpoint."""

    def test_delete_widget_success(self, client):
        """Test successful widget deletion."""
        # Create a widget
        widget_data = {"name": "Test Widget", "number_of_parts": 10}
        create_response = client.post("/widgets/", json=widget_data)
        widget_id = create_response.json()["id"]

        # Delete the widget
        response = client.delete(f"/widgets/{widget_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

        # Verify widget is deleted
        get_response = client.get(f"/widgets/{widget_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_widget_not_found(self, client):
        """Test deleting non-existent widget."""
        response = client.delete("/widgets/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["error"] == "WIDGET_NOT_FOUND"
        assert "message" in data
        assert "details" in data
        assert "widget_id" in data["details"]

    def test_delete_widget_invalid_id(self, client):
        """Test deleting widget with invalid ID format."""
        response = client.delete("/widgets/invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestWidgetAPIIntegration:
    """Test full CRUD cycles and integration scenarios."""

    def test_full_crud_cycle(self, client):
        """Test complete CRUD cycle for a widget."""
        # Create
        widget_data = {"name": "CRUD Test Widget", "number_of_parts": 7}
        create_response = client.post("/widgets/", json=widget_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        widget_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/widgets/{widget_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["name"] == "CRUD Test Widget"

        # Update
        update_data = {"name": "Updated CRUD Widget"}
        update_response = client.put(f"/widgets/{widget_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["name"] == "Updated CRUD Widget"

        # Delete
        delete_response = client.delete(f"/widgets/{widget_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        final_get_response = client.get(f"/widgets/{widget_id}")
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_widgets_management(self, client):
        """Test managing multiple widgets."""
        # Create multiple widgets
        widget_ids = []
        for i in range(3):
            widget_data = {"name": f"Widget {i}", "number_of_parts": i + 1}
            response = client.post("/widgets/", json=widget_data)
            widget_ids.append(response.json()["id"])

        # Verify all widgets exist in list
        list_response = client.get("/widgets/")
        assert len(list_response.json()["widgets"]) == 3

        # Update middle widget
        update_data = {"name": "Middle Widget Updated"}
        client.put(f"/widgets/{widget_ids[1]}", json=update_data)

        # Delete first widget
        client.delete(f"/widgets/{widget_ids[0]}")

        # Verify final state
        final_list_response = client.get("/widgets/")
        final_widgets = final_list_response.json()["widgets"]
        assert len(final_widgets) == 2

        # Find the updated widget
        updated_widget = next(
            w for w in final_widgets if w["id"] == widget_ids[1]
        )
        assert updated_widget["name"] == "Middle Widget Updated"


class TestOpenAPIDocumentation:
    """Test OpenAPI documentation and schema generation."""

    def test_openapi_schema_generation(self, client):
        """Test that OpenAPI schema is generated correctly."""
        response = client.get("/openapi.json")

        assert response.status_code == status.HTTP_200_OK
        schema = response.json()

        # Check basic structure
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        # Check widget endpoints are present
        paths = schema["paths"]
        assert "/widgets/" in paths
        assert "/widgets/{widget_id}" in paths

        # Check HTTP methods
        assert "post" in paths["/widgets/"]
        assert "get" in paths["/widgets/"]
        assert "get" in paths["/widgets/{widget_id}"]
        assert "put" in paths["/widgets/{widget_id}"]
        assert "delete" in paths["/widgets/{widget_id}"]

    def test_docs_endpoint_accessible(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_redoc_endpoint_accessible(self, client):
        """Test that ReDoc documentation is accessible."""
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
