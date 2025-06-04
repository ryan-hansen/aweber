import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import Connection, pool
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context  # type: ignore

# Add the src directory to Python path so we can import our models
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Import our models for autogenerate support
from app.database import Base  # noqa: E402
from app.models.widget import Widget  # noqa: E402, F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    # Create async engine
    connectable = create_async_engine(
        configuration["sqlalchemy.url"],
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Check if we're using an async URL
    url = config.get_main_option("sqlalchemy.url")
    if url and "+aiosqlite" in url:
        # Use async engine for aiosqlite
        asyncio.run(run_async_migrations())
    else:
        # Use sync engine for regular sqlite
        # Convert async URL to sync for migrations if needed
        sync_url = url.replace("+aiosqlite", "") if url else None
        configuration = config.get_section(config.config_ini_section, {})
        if sync_url:
            configuration["sqlalchemy.url"] = sync_url

        connectable = create_engine(
            sync_url or configuration.get("sqlalchemy.url", ""),
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
