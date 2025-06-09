# Widget CRUD API - Comprehensive Examples

This document provides detailed examples for all API endpoints with request/response examples.

## Base URL

```
http://localhost:8000
```

## Authentication

This API currently does not require authentication.

## Response Format

All responses are in JSON format. Error responses follow this structure:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## API Endpoints

### 1. Root Endpoint

**GET /** - Get API information

**Request:**
```bash
curl -X GET http://localhost:8000/
```

**Response:**
```json
{
  "message": "Welcome to Widget CRUD API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### 2. Health Check

**GET /health** - Check API health status

**Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Widget CRUD API"
}
```

---

### 3. Create Widget

**POST /widgets/** - Create a new widget

**Request:**
```bash
curl -X POST http://localhost:8000/widgets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Super Widget",
    "number_of_parts": 42
  }'
```

**Request Body Schema:**
```json
{
  "name": "string (required, max 64 characters)",
  "number_of_parts": "integer (required, positive)"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Super Widget",
  "number_of_parts": 42,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses:**
- **400 Bad Request** - Invalid input data
- **422 Unprocessable Entity** - Validation errors

---

### 4. List All Widgets

**GET /widgets/** - Retrieve all widgets with optional pagination

**Request:**
```bash
# Get all widgets
curl -X GET http://localhost:8000/widgets/

# With pagination (if implemented)
curl -X GET "http://localhost:8000/widgets/?skip=0&limit=10"
```

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Super Widget",
    "number_of_parts": 42,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  {
    "id": 2,
    "name": "Another Widget",
    "number_of_parts": 25,
    "created_at": "2024-01-01T13:00:00Z",
    "updated_at": "2024-01-01T13:00:00Z"
  }
]
```

---

### 5. Get Widget by ID

**GET /widgets/{widget_id}** - Retrieve a specific widget

**Request:**
```bash
curl -X GET http://localhost:8000/widgets/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Super Widget",
  "number_of_parts": 42,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses:**
- **404 Not Found** - Widget with specified ID does not exist

---

### 6. Update Widget

**PUT /widgets/{widget_id}** - Update an existing widget

**Request:**
```bash
curl -X PUT http://localhost:8000/widgets/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Super Widget",
    "number_of_parts": 50
  }'
```

**Request Body Schema:**
```json
{
  "name": "string (required, max 64 characters)",
  "number_of_parts": "integer (required, positive)"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Updated Super Widget",
  "number_of_parts": 50,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T14:00:00Z"
}
```

**Error Responses:**
- **404 Not Found** - Widget with specified ID does not exist
- **400 Bad Request** - Invalid input data
- **422 Unprocessable Entity** - Validation errors

---

### 7. Delete Widget

**DELETE /widgets/{widget_id}** - Delete a widget

**Request:**
```bash
curl -X DELETE http://localhost:8000/widgets/1
```

**Response (204 No Content):**
No response body

**Error Responses:**
- **404 Not Found** - Widget with specified ID does not exist

---

## Complete Usage Examples

### Example 1: Basic CRUD Operations

```bash
# 1. Create a widget
curl -X POST http://localhost:8000/widgets/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Widget", "number_of_parts": 10}'

# 2. Get the widget (assuming ID 1)
curl -X GET http://localhost:8000/widgets/1

# 3. Update the widget
curl -X PUT http://localhost:8000/widgets/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Test Widget", "number_of_parts": 15}'

# 4. List all widgets
curl -X GET http://localhost:8000/widgets/

# 5. Delete the widget
curl -X DELETE http://localhost:8000/widgets/1
```

### Example 2: Error Handling

```bash
# Try to get a non-existent widget
curl -X GET http://localhost:8000/widgets/999
# Response: {"detail": "Widget not found"}

# Try to create a widget with invalid data
curl -X POST http://localhost:8000/widgets/ \
  -H "Content-Type: application/json" \
  -d '{"name": "", "number_of_parts": -1}'
# Response: {"detail": [{"loc": ["body", "name"], "msg": "ensure this value has at least 1 characters", "type": "value_error.any_str.min_length"}]}
```

### Example 3: Using Python requests

```python
import requests
import json

base_url = "http://localhost:8000"

# Create a widget
widget_data = {
    "name": "Python Widget",
    "number_of_parts": 25
}

response = requests.post(f"{base_url}/widgets/", json=widget_data)
if response.status_code == 201:
    widget = response.json()
    print(f"Created widget with ID: {widget['id']}")

    # Get the widget
    get_response = requests.get(f"{base_url}/widgets/{widget['id']}")
    print(f"Retrieved widget: {get_response.json()}")

    # Update the widget
    update_data = {
        "name": "Updated Python Widget",
        "number_of_parts": 30
    }
    update_response = requests.put(f"{base_url}/widgets/{widget['id']}", json=update_data)
    print(f"Updated widget: {update_response.json()}")

    # Delete the widget
    delete_response = requests.delete(f"{base_url}/widgets/{widget['id']}")
    print(f"Delete status: {delete_response.status_code}")
```

### Example 4: Using JavaScript/fetch

```javascript
const baseUrl = 'http://localhost:8000';

async function widgetExample() {
    try {
        // Create widget
        const createResponse = await fetch(`${baseUrl}/widgets/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: 'JavaScript Widget',
                number_of_parts: 20
            })
        });

        const widget = await createResponse.json();
        console.log('Created widget:', widget);

        // Get widget
        const getResponse = await fetch(`${baseUrl}/widgets/${widget.id}`);
        const retrievedWidget = await getResponse.json();
        console.log('Retrieved widget:', retrievedWidget);

        // Update widget
        const updateResponse = await fetch(`${baseUrl}/widgets/${widget.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: 'Updated JavaScript Widget',
                number_of_parts: 25
            })
        });

        const updatedWidget = await updateResponse.json();
        console.log('Updated widget:', updatedWidget);

        // Delete widget
        const deleteResponse = await fetch(`${baseUrl}/widgets/${widget.id}`, {
            method: 'DELETE'
        });

        console.log('Delete status:', deleteResponse.status);

    } catch (error) {
        console.error('Error:', error);
    }
}

widgetExample();
```

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting based on your requirements.

## CORS

Cross-Origin Resource Sharing (CORS) may be configured for the API. Check with your administrator for allowed origins.

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
