"""Tests for Config."""

import os
import tempfile
import pytest

from backend.core.config import Config


def test_env_file_loading():
    fd, path = tempfile.mkstemp(suffix=".env")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("TEST_KEY=test_value\n")
            f.write("# comment\n")
            f.write("OTHER_KEY=other\n")

        c = Config(env_file=path)
        assert c.get("TEST_KEY") == "test_value"
        assert c.get("OTHER_KEY") == "other"
    finally:
        os.unlink(path)


def test_get_with_default(container):
    assert container.get("config").get("NONEXISTENT", "fallback") == "fallback"


def test_get_required_missing(container):
    config = container.get("config")
    with pytest.raises(RuntimeError, match="not set"):
        config.get_required("NONEXISTENT_REQUIRED_KEY")


def test_set_override(container):
    config = container.get("config")
    config.set("NEW_KEY", "new_value")
    assert config.get("NEW_KEY") == "new_value"
