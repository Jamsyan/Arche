"""Settings module for Arche backend."""

from __future__ import annotations

from .app import AppSettings
from .base import PluginSettingsBase

__all__ = [
    "AppSettings",
    "PluginSettingsBase",
]
