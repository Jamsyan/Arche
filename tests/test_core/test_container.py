"""Tests for ServiceContainer."""

import pytest

from backend.core.container import ServiceContainer, CircularDependencyError, ServiceNotFoundError


def test_register_and_get(container):
    container.register("test", lambda c: "hello")
    assert container.get("test") == "hello"


def test_lazy_creation(container):
    """服务在 get() 时才创建。"""
    created = []
    container.register("lazy", lambda c: created.append(1) or "done")
    assert len(created) == 0  # 未 get，未创建
    container.get("lazy")
    assert len(created) == 1  # get 后创建


def test_singleton(container):
    """多次 get 返回同一实例。"""
    container.register("obj", lambda c: object())
    a = container.get("obj")
    b = container.get("obj")
    assert a is b


def test_circular_dependency():
    """A -> B -> A 循环依赖应抛出异常。"""
    c = ServiceContainer()
    c.register("a", lambda con: con.get("b"))
    c.register("b", lambda con: con.get("a"))
    with pytest.raises(CircularDependencyError):
        c.get("a")


def test_is_available(container):
    assert container.is_available("config") is True
    assert container.is_available("nonexistent") is False


def test_missing_service(container):
    with pytest.raises(ServiceNotFoundError):
        container.get("nonexistent")


def test_shutdown(container):
    """shutdown 时调用有 close 方法的实例。"""
    closed = []

    class Closable:
        def close(self):
            closed.append(True)

    container.register("closable", lambda c: Closable())
    container.get("closable")
    container.shutdown()
    assert closed == [True]
