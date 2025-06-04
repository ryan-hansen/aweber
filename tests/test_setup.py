"""Test module to verify project setup and dependencies."""

import sys

import pytest


def test_python_version() -> None:
    """Test that Python 3.12 is being used."""
    assert sys.version_info.major == 3
    assert sys.version_info.minor == 12


def test_fastapi_import() -> None:
    """Test that FastAPI can be imported successfully."""
    try:
        import fastapi  # noqa: F401
    except ImportError:
        pytest.fail("FastAPI could not be imported")


def test_sqlalchemy_import() -> None:
    """Test that SQLAlchemy can be imported successfully."""
    try:
        import sqlalchemy  # noqa: F401
    except ImportError:
        pytest.fail("SQLAlchemy could not be imported")


def test_pydantic_import() -> None:
    """Test that Pydantic can be imported successfully."""
    try:
        import pydantic  # noqa: F401
    except ImportError:
        pytest.fail("Pydantic could not be imported")


def test_alembic_import() -> None:
    """Test that Alembic can be imported successfully."""
    try:
        import alembic  # noqa: F401
    except ImportError:
        pytest.fail("Alembic could not be imported")


@pytest.mark.asyncio
async def test_async_support() -> None:
    """Test that async functionality is working."""

    async def dummy_async_function() -> str:
        return "async working"

    result = await dummy_async_function()
    assert result == "async working"
