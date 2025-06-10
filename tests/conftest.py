"""
Pytest configuration and shared fixtures for the test suite.

This module configures the test environment and provides shared fixtures
for database setup, test client, and common test utilities.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response

# Add the project root to Python path to enable imports from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# noqa: E402 - imports below must come after sys.path modification
from src.app.database import (  # noqa: E402
    create_test_tables,
    drop_test_tables,
    get_db,
    get_test_db,
)
from src.app.main import create_app  # noqa: E402


@pytest.fixture
def test_app():
    """Create test FastAPI application with test database override."""
    app = create_app()
    # Override the database dependency to use test database
    app.dependency_overrides[get_db] = get_test_db
    return app


@pytest.fixture
def client(test_app):
    """Create test client for FastAPI application."""
    return TestClient(test_app)


@pytest.fixture(autouse=True, scope="function")
def setup_test_db():
    """Set up clean test database for each test function."""
    # Clean up before each test
    asyncio.run(drop_test_tables())
    asyncio.run(create_test_tables())
    yield
    # Clean up after each test
    asyncio.run(drop_test_tables())


@pytest.fixture
def sample_widget_data():
    """Provide sample widget data for testing."""
    return {
        "name": "Test Widget",
        "number_of_parts": 10,
    }


@pytest.fixture
def multiple_widget_data():
    """Provide multiple widget data sets for testing."""
    return [
        {"name": "Widget A", "number_of_parts": 5},
        {"name": "Widget B", "number_of_parts": 10},
        {"name": "Widget C", "number_of_parts": 15},
        {"name": "Widget D", "number_of_parts": 20},
        {"name": "Widget E", "number_of_parts": 25},
    ]


@pytest.fixture
def mock_request():
    """Create a mock request object for testing."""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.__str__ = Mock(return_value="http://test.com/api/widgets")
    request.url.path = "/api/widgets"
    request.method = "GET"
    request.state = Mock()
    request.state.request_id = "test-123"
    request.client = Mock()
    request.client.host = "127.0.0.1"
    request.headers = {"content-type": "application/json"}
    return request


@pytest.fixture
def mock_response():
    """Create a mock response object for testing."""
    response = Mock(spec=Response)
    response.status_code = 200
    response.headers = {}
    return response


@pytest.fixture
def app_with_middleware():
    """Create a FastAPI app with middleware for testing."""
    app = FastAPI()
    # Import middleware here to avoid circular imports
    from src.app.middleware import RequestLoggingMiddleware

    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.get("/test/error")
    async def test_error_endpoint():
        raise ValueError("Test error")

    return app
