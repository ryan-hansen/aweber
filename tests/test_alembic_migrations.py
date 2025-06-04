"""
Tests for Alembic database migrations.
"""

import os
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Create a temporary database for testing migrations."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db_path = f.name

    # Update alembic.ini to use temp database
    original_db = None
    alembic_ini_path = Path("alembic.ini")
    if alembic_ini_path.exists():
        content = alembic_ini_path.read_text()
        # Find the sqlalchemy.url line
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("sqlalchemy.url"):
                original_db = line
                lines[i] = f"sqlalchemy.url = sqlite:///{temp_db_path}"
                break

        # Write updated content
        alembic_ini_path.write_text("\n".join(lines))

    yield temp_db_path

    # Cleanup: restore original database URL and remove temp file
    if original_db and alembic_ini_path.exists():
        content = alembic_ini_path.read_text()
        content = content.replace(
            f"sqlite:///{temp_db_path}", original_db.split("=", 1)[1].strip()
        )
        alembic_ini_path.write_text(content)

    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


def test_alembic_ini_exists() -> None:
    """Test that alembic.ini configuration file exists."""
    alembic_ini = Path("alembic.ini")
    assert alembic_ini.exists(), "alembic.ini should exist"


def test_alembic_directory_structure() -> None:
    """Test that Alembic directory structure is properly set up."""
    alembic_dir = Path("alembic")
    assert alembic_dir.exists(), "alembic directory should exist"
    assert (alembic_dir / "env.py").exists(), "env.py should exist"
    assert (
        alembic_dir / "script.py.mako"
    ).exists(), "script.py.mako should exist"
    assert (
        alembic_dir / "versions"
    ).exists(), "versions directory should exist"


def test_alembic_env_imports() -> None:
    """Test that env.py can import our models correctly."""
    # This test verifies that the env.py configuration is correct
    import sys
    from pathlib import Path

    # Add src to path (same as env.py does)
    sys.path.append(str(Path(__file__).parent.parent / "src"))

    try:
        from app.database import Base  # noqa: F401
        from app.models.widget import Widget  # noqa: F401

        assert True, "Models imported successfully"
    except ImportError as e:
        assert False, f"Failed to import models: {e}"


def test_migration_file_exists() -> None:
    """Test that at least one migration file exists."""
    versions_dir = Path("alembic/versions")
    migration_files = list(versions_dir.glob("*.py"))
    migration_files = [
        f for f in migration_files if not f.name.startswith("__")
    ]
    assert len(migration_files) > 0, "At least one migration file should exist"


def test_migration_upgrade_command() -> None:
    """Test that alembic upgrade command works."""
    result = subprocess.run(
        ["poetry", "run", "alembic", "check"], capture_output=True, text=True
    )
    # alembic check returns 0 if migrations are up to date
    assert result.returncode == 0, f"Alembic check failed: {result.stderr}"


def test_migration_creates_widget_table(temp_db: str) -> None:
    """Test that migration creates the widget table with correct structure."""
    # Run migration on temp database
    result = subprocess.run(
        ["poetry", "run", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Migration failed: {result.stderr}"

    # Check table structure
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Check table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='widgets'"
    )
    table_exists = cursor.fetchone()
    assert table_exists, "widgets table should be created"

    # Check table structure
    cursor.execute("PRAGMA table_info(widgets)")
    columns = cursor.fetchall()

    expected_columns = {
        "id": ("INTEGER", 1, 1),  # (type, not_null, primary_key)
        "name": ("VARCHAR(64)", 1, 0),
        "number_of_parts": ("INTEGER", 1, 0),
        "created_at": ("DATETIME", 1, 0),
        "updated_at": ("DATETIME", 1, 0),
    }

    for col in columns:
        col_name = col[1]
        col_type = col[2]
        not_null = col[3]
        primary_key = col[5]

        assert col_name in expected_columns, f"Unexpected column: {col_name}"
        expected_type, expected_not_null, expected_pk = expected_columns[
            col_name
        ]
        assert (
            col_type == expected_type
        ), f"Wrong type for {col_name}: {col_type}"
        assert not_null == expected_not_null, f"Wrong not_null for {col_name}"
        assert primary_key == expected_pk, f"Wrong primary_key for {col_name}"

    conn.close()


def test_migration_creates_indexes(temp_db: str) -> None:
    """Test that migration creates the expected indexes."""
    # Run migration on temp database
    result = subprocess.run(
        ["poetry", "run", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Migration failed: {result.stderr}"

    # Check indexes
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='index' AND tbl_name='widgets'"
    )
    indexes = [row[0] for row in cursor.fetchall()]

    expected_indexes = ["ix_widgets_created_at", "ix_widgets_name"]
    for expected_index in expected_indexes:
        assert (
            expected_index in indexes
        ), f"Index {expected_index} should exist"

    conn.close()


def test_migration_downgrade_works(temp_db: str) -> None:
    """Test that migration downgrade removes the table."""
    # First upgrade
    result = subprocess.run(
        ["poetry", "run", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Migration upgrade failed: {result.stderr}"

    # Then downgrade
    result = subprocess.run(
        ["poetry", "run", "alembic", "downgrade", "base"],
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"Migration downgrade failed: {result.stderr}"

    # Check table is gone
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='widgets'"
    )
    table_exists = cursor.fetchone()
    assert not table_exists, "widgets table should be removed after downgrade"

    conn.close()


def test_alembic_current_shows_version() -> None:
    """Test that alembic current command shows the current version."""
    result = subprocess.run(
        ["poetry", "run", "alembic", "current"], capture_output=True, text=True
    )
    assert result.returncode == 0, f"Alembic current failed: {result.stderr}"
    # Should show a revision ID (not empty)
    assert result.stdout.strip(), "Should show current revision"


def test_alembic_history_shows_migrations() -> None:
    """Test that alembic history command shows migration history."""
    result = subprocess.run(
        ["poetry", "run", "alembic", "history"], capture_output=True, text=True
    )
    assert result.returncode == 0, f"Alembic history failed: {result.stderr}"
    # Should show at least one migration
    assert (
        "Create widget table" in result.stdout
    ), "Should show widget table migration"


def test_alembic_configuration_valid() -> None:
    """Test that Alembic configuration is valid."""
    # Test that alembic can validate the configuration
    result = subprocess.run(
        ["poetry", "run", "alembic", "check"], capture_output=True, text=True
    )
    assert (
        result.returncode == 0
    ), f"Alembic configuration invalid: {result.stderr}"

    # Test that env.py file exists and has the right content
    env_py = Path("alembic/env.py")
    assert env_py.exists(), "env.py should exist"

    content = env_py.read_text()
    assert "from app.database import Base" in content, "Should import Base"
    assert (
        "from app.models.widget import Widget" in content
    ), "Should import Widget"
    assert (
        "target_metadata = Base.metadata" in content
    ), "Should set target_metadata"
