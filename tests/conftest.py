"""Shared test fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.container import ServiceContainer
from backend.core.config import Config


@pytest.fixture
def config():
    """Test config with default values."""
    c = Config()
    c.set("DATABASE_URL", "sqlite+aiosqlite:///./test_veil.db")
    c.set("SECRET_KEY", "test-secret-key")
    return c


@pytest.fixture
def container(config):
    """Empty service container with config registered."""
    c = ServiceContainer()
    c.register("config", lambda _: config)
    return c
