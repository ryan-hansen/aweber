"""
Tests to verify Poetry migration and dependency management.
"""

import subprocess
import sys
from pathlib import Path


def test_pyproject_toml_exists() -> None:
    """Test that pyproject.toml exists."""
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml should exist"


def test_poetry_lock_exists() -> None:
    """Test that poetry.lock exists."""
    lock_path = Path("poetry.lock")
    assert lock_path.exists(), "poetry.lock should exist"


def test_requirements_txt_removed() -> None:
    """Test that requirements.txt was removed."""
    requirements_path = Path("requirements.txt")
    assert not requirements_path.exists(), "requirements.txt should be removed"


def test_poetry_commands_work() -> None:
    """Test that basic Poetry commands work."""
    # Test poetry show (list dependencies)
    result = subprocess.run(
        [sys.executable, "-m", "poetry", "show"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    assert result.returncode == 0, f"poetry show failed: {result.stderr}"
    assert "fastapi" in result.stdout.lower()
    assert "pytest" in result.stdout.lower()


def test_core_dependencies_installed() -> None:
    """Test that core dependencies are installed correctly."""
    try:
        import fastapi  # noqa: F401
        import sqlalchemy  # noqa: F401
        import pydantic  # noqa: F401
        import uvicorn  # noqa: F401

        assert True, "Core dependencies imported successfully"
    except ImportError as e:
        assert False, f"Failed to import core dependency: {e}"


def test_dev_dependencies_installed() -> None:
    """Test that development dependencies are installed correctly."""
    try:
        import pytest  # noqa: F401
        import coverage  # noqa: F401
        import flake8  # noqa: F401
        import black  # noqa: F401
        import bandit  # noqa: F401
        import mypy  # noqa: F401

        assert True, "Dev dependencies imported successfully"
    except ImportError as e:
        assert False, f"Failed to import dev dependency: {e}"


def test_dependency_groups_configured() -> None:
    """Test that dependency groups are properly configured."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    assert "[tool.poetry.dependencies]" in content
    assert "[tool.poetry.group.dev.dependencies]" in content
    assert "fastapi" in content
    assert "pytest" in content


def test_python_version_constraint() -> None:
    """Test that Python version constraint is set correctly."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    assert 'python = "^3.12"' in content


def test_black_configuration_preserved() -> None:
    """Test that Black configuration was preserved."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    assert "[tool.black]" in content
    assert "line-length = 79" in content
    assert "target-version = ['py312']" in content


def test_package_metadata_configured() -> None:
    """Test that package metadata is configured correctly."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    assert 'name = "widget-crud-api"' in content
    assert 'version = "1.0.0"' in content
    assert "Widget CRUD REST API" in content
