"""
Plugin Registry - Central hub for loading and activating plugins.

Plugins are self-contained modules that register themselves with the registry.
The core does NOT know about plugin specifics — it only knows the registry.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


class PluginRegistry:
    """Singleton registry that manages plugin lifecycle."""

    def __init__(self):
        self._plugins: dict[str, object] = {}
        self._active: list[str] = []

    def register(self, name: str, plugin: object) -> None:
        """Register a plugin instance. Does NOT activate it."""
        self._plugins[name] = plugin

    def activate(self, name: str, app: FastAPI) -> None:
        """Activate a registered plugin, mounting its routes."""
        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' not registered")
        plugin = self._plugins[name]
        if hasattr(plugin, "setup"):
            plugin.setup(app)
        self._active.append(name)

    def activate_all(self, app: FastAPI) -> None:
        """Activate all registered plugins."""
        for name in list(self._plugins):
            self.activate(name, app)

    @property
    def active(self) -> list[str]:
        return list(self._active)

    @property
    def available(self) -> list[str]:
        return list(self._plugins)


registry = PluginRegistry()


def discover_plugins(plugin_dir: Path | None = None) -> None:
    """Auto-discover and import all plugin directories under the plugin dir.

    Each plugin must be a subdirectory containing an __init__.py.
    """
    if plugin_dir is None:
        plugin_dir = Path(__file__).resolve().parent.parent / "plugins"
    for entry in plugin_dir.iterdir():
        if not entry.is_dir():
            continue
        init_file = entry / "__init__.py"
        if not init_file.exists():
            continue
        module_name = f"backend.plugins.{entry.name}"
        import_module(module_name)
