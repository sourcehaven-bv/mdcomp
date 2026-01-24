"""Pytest fixtures for mdcomp tests."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def snippets_dir(fixtures_dir: Path) -> Path:
    """Return the path to the test snippets directory."""
    return fixtures_dir / "snippets"


@pytest.fixture
def templates_dir(fixtures_dir: Path) -> Path:
    """Return the path to the test templates directory."""
    return fixtures_dir / "templates"


@pytest.fixture
def context_file(fixtures_dir: Path) -> Path:
    """Return the path to the test context file."""
    return fixtures_dir / "context.yaml"
