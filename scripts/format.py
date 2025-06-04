#!/usr/bin/env python3
"""
Code formatting script.

Runs isort and black to ensure consistent code formatting.
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
        print(f"✅ {description} completed successfully")
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
    """Run all formatting tools."""
    print("🎨 Starting code formatting...")

    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"

    success = True

    # Run isort
    success &= run_command(
        ["isort", str(src_dir), str(tests_dir)], "isort (import sorting)"
    )

    # Run black
    success &= run_command(
        ["black", str(src_dir), str(tests_dir)], "black (code formatting)"
    )

    if success:
        print("🎉 All formatting completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some formatting tools failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
