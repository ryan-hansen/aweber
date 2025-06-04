"""Test FastAPI application structure and configuration."""

import os
import sys
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app  # noqa: E402
from app.config import Settings, get_settings  # noqa: E402
from app.main import create_app  # noqa: E402


class TestApplicationConfiguration:
    """Test application configuration."""

    def test_settings_defaults(self) -> None:
        """Test that settings have correct default values."""
        settings = Settings()

        assert settings.app_name == "Widget CRUD API"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.database_url == "sqlite+aiosqlite:///./widgets.db"
        assert settings.test_database_url == "sqlite+aiosqlite:///./test_widgets.db"
        assert settings.api_v1_prefix == "/api/v1"
        assert settings.docs_url == "/docs"
        assert settings.redoc_url == "/redoc"
        assert settings.openapi_url == "/openapi.json"
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:8080" in settings.cors_origins

    def test_settings_from_env(self) -> None:
        """Test that settings can be loaded from environment variables."""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "Test API",
                "APP_VERSION": "0.1.0",
                "DEBUG": "true",
                "DATABASE_URL": "sqlite:///test.db",
            },
        ):
            settings = Settings()

            assert settings.app_name == "Test API"
            assert settings.app_version == "0.1.0"
            assert settings.debug is True
            assert settings.database_url == "sqlite:///test.db"

    def test_get_settings_cached(self) -> None:
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2


class TestFastAPIApplication:
    """Test FastAPI application setup."""

    def test_app_creation(self) -> None:
        """Test that FastAPI app is created correctly."""
        test_app = create_app()

        assert isinstance(test_app, FastAPI)
        assert test_app.title == "Widget CRUD API"
        assert test_app.version == "1.0.0"
        assert "Widget" in test_app.description

    def test_app_instance_exists(self) -> None:
        """Test that app instance is available."""
        assert isinstance(app, FastAPI)

    def test_openapi_schema(self) -> None:
        """Test that OpenAPI schema is generated."""
        with TestClient(app) as client:
            response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "Widget CRUD API"
        assert schema["info"]["version"] == "1.0.0"

    def test_docs_endpoint(self) -> None:
        """Test that documentation endpoint is accessible."""
        with TestClient(app) as client:
            response = client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint(self) -> None:
        """Test that ReDoc endpoint is accessible."""
        with TestClient(app) as client:
            response = client.get("/redoc")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestAPIEndpoints:
    """Test basic API endpoints."""

    def test_root_endpoint(self) -> None:
        """Test root endpoint."""
        with TestClient(app) as client:
            response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Widget CRUD API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"

    def test_health_check_endpoint(self) -> None:
        """Test health check endpoint."""
        with TestClient(app) as client:
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Widget CRUD API"


class TestCORSMiddleware:
    """Test CORS middleware configuration."""

    def test_cors_headers(self) -> None:
        """Test that CORS headers are set correctly."""
        with TestClient(app) as client:
            response = client.options(
                "/",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers


class TestErrorHandling:
    """Test global error handling."""

    def test_404_error(self) -> None:
        """Test 404 error handling."""
        with TestClient(app) as client:
            response = client.get("/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_lifespan_events() -> None:
    """Test application lifespan events."""
    # This test verifies that the lifespan context manager is properly configured
    # The actual startup/shutdown behavior is tested through the app instance
    test_app = create_app()
    assert test_app.router.lifespan_context is not None
