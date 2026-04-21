"""Service container — lazy registration, retrieval, and circular dependency detection."""

from __future__ import annotations

from typing import Callable


class CircularDependencyError(Exception):
    pass


class ServiceNotFoundError(Exception):
    pass


class ServiceContainer:
    """Lightweight IoC container with lazy instantiation and cycle detection."""

    def __init__(self):
        self._factories: dict[str, Callable] = {}
        self._instances: dict[str, object] = {}
        self._resolving: list[str] = []

    def register(self, name: str, factory: Callable) -> None:
        self._factories[name] = factory

    def get(self, name: str) -> object:
        if name in self._resolving:
            cycle = " -> ".join(self._resolving + [name])
            raise CircularDependencyError(f"循环依赖: {cycle}")
        if name not in self._factories:
            raise ServiceNotFoundError(f"服务 '{name}' 未注册")
        if name not in self._instances:
            self._resolving.append(name)
            try:
                self._instances[name] = self._factories[name](self)
            finally:
                self._resolving.remove(name)
        return self._instances[name]

    def is_available(self, name: str) -> bool:
        return name in self._factories

    def shutdown(self) -> None:
        for instance in reversed(list(self._instances.values())):
            if hasattr(instance, "close"):
                instance.close()
