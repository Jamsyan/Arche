"""
BasePlugin - Abstract interface that all plugins must implement.

Each plugin:
1. Inherits from BasePlugin
2. Implements the setup() method to register routes
3. Registers itself with the global registry in its module-level init
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


class BasePlugin(ABC):
    """All plugins inherit from this."""

    name: str = ""
    version: str = "0.1.0"

    @abstractmethod
    def setup(self, app: "FastAPI") -> None:
        """Called during app startup. Register routes, middleware, etc. here."""
        ...
