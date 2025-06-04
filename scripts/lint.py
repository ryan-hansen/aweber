#!/usr/bin/env python3
"""
Code linting script.

Runs all code quality checks: flake8, bandit, mypy, and tests.
"""
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(  # nosec B603
            command, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} passed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main() -> None:
    """Run all linting tools."""
    print("🔍 Starting code quality checks...")

    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"

    success = True

    # Check formatting first
    success &= run_command(
        ["black", "--check", str(src_dir), str(tests_dir)],
        "black (formatting check)",
    )

    success &= run_command(
        ["isort", "--check-only", str(src_dir), str(tests_dir)],
        "isort (import order check)",
    )

    # Run linting
    success &= run_command(
        ["flake8", str(src_dir), str(tests_dir)],
        "flake8 (style and error checking)",
    )

    # Run security check
    success &= run_command(
        ["bandit", "-r", str(src_dir)], "bandit (security analysis)"
    )

    # Run type checking
    success &= run_command(["mypy", str(src_dir)], "mypy (type checking)")

    # Run tests with proper Python path
    import os

    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

    print("Running pytest (unit tests)...")
    try:
        result = subprocess.run(  # nosec B603 B607
            ["pytest", str(tests_dir), "-v"],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        print("✅ pytest (unit tests) passed")
        if result.stdout:
            print(result.stdout)
        success &= True
    except subprocess.CalledProcessError as e:
        print("❌ pytest (unit tests) failed")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        success &= False

    if success:
        print("🎉 All quality checks passed!")
        sys.exit(0)
    else:
        print("💥 Some quality checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
