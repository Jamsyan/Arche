"""Tests for PluginRegistry."""

import pytest

from backend.core.plugin_registry import PluginRegistry, DependencyError
from backend.core.base_plugin import BasePlugin


class MockPlugin(BasePlugin):
    name = "mock"
    version = "0.1.0"
    requires = []
    optional = []

    def setup(self, app):
        self._setup_called = True


class DepPlugin(BasePlugin):
    name = "dep"
    requires = ["mock"]
    optional = []

    def setup(self, app):
        self._setup_called = True


def test_register_and_activate():
    registry = PluginRegistry()
    plugin = MockPlugin()
    registry.register("mock", plugin)
    assert "mock" in registry.available


def test_topological_order():
    registry = PluginRegistry()
    mock = MockPlugin()
    dep = DepPlugin()
    registry.register("mock", mock)
    registry.register("dep", dep)

    ordered = registry._topological_sort()
    # mock 必须在 dep 前面
    assert ordered.index("mock") < ordered.index("dep")


def test_missing_hard_dependency():
    registry = PluginRegistry()

    class NeedsMissing(BasePlugin):
        name = "needsmissing"
        requires = ["nonexistent"]

        def setup(self, app):
            pass

    registry.register("needsmissing", NeedsMissing())
    with pytest.raises(DependencyError, match="nonexistent"):
        registry._topological_sort()


def test_optional_dependency_graceful():
    """软依赖不存在不影响排序。"""
    registry = PluginRegistry()

    class SoftDep(BasePlugin):
        name = "softdep"
        optional = ["nonexistent"]

        def setup(self, app):
            pass

    registry.register("softdep", SoftDep())
    ordered = registry._topological_sort()
    assert "softdep" in ordered


def test_circular_dependency_detection():
    registry = PluginRegistry()

    class A(BasePlugin):
        name = "a"
        requires = ["b"]
        def setup(self, app): pass

    class B(BasePlugin):
        name = "b"
        requires = ["a"]
        def setup(self, app): pass

    registry.register("a", A())
    registry.register("b", B())
    with pytest.raises(DependencyError, match="循环依赖"):
        registry._topological_sort()
