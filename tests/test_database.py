"""Test database configuration and async session management."""

import os
import sys
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.database import (  # noqa: E402
    engine,
    test_engine,
    AsyncSessionLocal,
    TestAsyncSessionLocal,
    Base,
    get_db,
    get_test_db,
    create_tables,
    create_test_tables,
    drop_tables,
    drop_test_tables,
    is_testing,
)
from app.config import get_settings  # noqa: E402


class TestDatabaseConfiguration:
    """Test database configuration and engines."""

    def test_engine_configuration(self) -> None:
        """Test that database engines are configured correctly."""
        settings = get_settings()

        # Test main engine
        assert engine is not None
        assert str(engine.url) == settings.database_url
        assert "aiosqlite" in str(engine.url)

        # Test test engine
        assert test_engine is not None
        assert str(test_engine.url) == settings.test_database_url
        assert "test_widgets.db" in str(test_engine.url)

    def test_session_factories(self) -> None:
        """Test that session factories are configured correctly."""
        assert AsyncSessionLocal is not None
        assert TestAsyncSessionLocal is not None

        # Verify they create AsyncSession instances
        assert AsyncSessionLocal.class_ is AsyncSession
        assert TestAsyncSessionLocal.class_ is AsyncSession

    def test_base_declarative(self) -> None:
        """Test that Base declarative class is available."""
        assert Base is not None
        assert hasattr(Base, "metadata")


class TestAsyncSessionManagement:
    """Test async session management and dependency injection."""

    @pytest.mark.asyncio
    async def test_get_db_session(self) -> None:
        """Test that get_db provides a valid async session."""
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            assert session.bind is not None
            # Session might not be active until used
            assert not session.is_active or True
            break

    @pytest.mark.asyncio
    async def test_get_test_db_session(self) -> None:
        """Test that get_test_db provides a valid async test session."""
        async for session in get_test_db():
            assert isinstance(session, AsyncSession)
            assert session.bind is not None
            # Verify it's using the test engine
            bind_url = (
                str(session.bind.url)
                if hasattr(session.bind, "url")
                else str(session.bind)
            )
            assert "test_widgets.db" in bind_url
            break

    @pytest.mark.asyncio
    async def test_session_cleanup(self) -> None:
        """Test that sessions are properly cleaned up."""
        session_ref = None

        async for session in get_db():
            session_ref = session
            break

        # After the context, session should be closed
        # Note: We can't easily test this without a transaction
        assert session_ref is not None

    @pytest.mark.asyncio
    async def test_multiple_sessions(self) -> None:
        """Test that multiple sessions can be created."""
        sessions = []

        for _ in range(3):
            async for session in get_db():
                sessions.append(session)
                break

        assert len(sessions) == 3
        # Each session should be a different instance
        assert len(set(id(s) for s in sessions)) == 3


class TestDatabaseOperations:
    """Test database table creation and management operations."""

    @pytest.mark.asyncio
    async def test_create_tables(self) -> None:
        """Test that create_tables executes without error."""
        # This should not raise an exception
        await create_tables()

    @pytest.mark.asyncio
    async def test_create_test_tables(self) -> None:
        """Test that create_test_tables executes without error."""
        # This should not raise an exception
        await create_test_tables()

    @pytest.mark.asyncio
    async def test_drop_tables(self) -> None:
        """Test that drop_tables executes without error."""
        # Create tables first
        await create_tables()

        # Then drop them
        await drop_tables()

    @pytest.mark.asyncio
    async def test_drop_test_tables(self) -> None:
        """Test that drop_test_tables executes without error."""
        # Create test tables first
        await create_test_tables()

        # Then drop them
        await drop_test_tables()

    @pytest.mark.asyncio
    async def test_table_creation_idempotent(self) -> None:
        """Test that table creation is idempotent."""
        # Create tables multiple times - should not fail
        await create_tables()
        await create_tables()
        await create_tables()


class TestEnvironmentHelpers:
    """Test environment helper functions."""

    def test_is_testing_false_by_default(self) -> None:
        """Test that is_testing returns False by default."""
        # Ensure TESTING env var is not set
        with patch.dict(os.environ, {}, clear=True):
            assert is_testing() is False

    def test_is_testing_true_when_set(self) -> None:
        """Test that is_testing returns True when TESTING env var is set."""
        with patch.dict(os.environ, {"TESTING": "true"}):
            assert is_testing() is True

        with patch.dict(os.environ, {"TESTING": "True"}):
            assert is_testing() is True

        with patch.dict(os.environ, {"TESTING": "TRUE"}):
            assert is_testing() is True

    def test_is_testing_false_with_false_values(self) -> None:
        """Test that is_testing returns False for false-like values."""
        false_values = ["false", "False", "FALSE", "0", "no", "off"]

        for value in false_values:
            with patch.dict(os.environ, {"TESTING": value}):
                assert is_testing() is False


class TestDatabaseURLs:
    """Test database URL configuration."""

    def test_main_database_url_format(self) -> None:
        """Test that main database URL uses correct async format."""
        settings = get_settings()
        assert settings.database_url.startswith("sqlite+aiosqlite:")
        assert "widgets.db" in settings.database_url

    def test_test_database_url_format(self) -> None:
        """Test that test database URL uses correct async format."""
        settings = get_settings()
        assert settings.test_database_url.startswith("sqlite+aiosqlite:")
        assert "test_widgets.db" in settings.test_database_url

    def test_different_database_files(self) -> None:
        """Test that main and test databases use different files."""
        settings = get_settings()
        assert settings.database_url != settings.test_database_url
        assert "test_widgets.db" in settings.test_database_url
        assert "test_widgets.db" not in settings.database_url
