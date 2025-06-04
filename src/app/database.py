"""Database configuration and session management for async SQLAlchemy 2.0."""

from typing import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

from .config import get_settings

settings = get_settings()

# Create async SQLAlchemy engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    future=True,
)

# Create test engine for testing
test_engine = create_async_engine(
    settings.test_database_url,
    echo=settings.debug,
    future=True,
)

# Create async session factories
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.

    This function provides a database session for dependency injection
    in FastAPI route handlers. It automatically manages session lifecycle,
    ensuring proper cleanup.

    Yields:
        AsyncSession: SQLAlchemy async session for database operations.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async test database session.

    Used during testing to provide isolated database sessions
    that don't interfere with production data.

    Yields:
        AsyncSession: SQLAlchemy async session for test database operations.
    """
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables() -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_test_tables() -> None:
    """Create all test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def drop_test_tables() -> None:
    """Drop all test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def is_testing() -> bool:
    """Check if we're running in test mode."""
    return os.getenv("TESTING", "false").lower() == "true"
