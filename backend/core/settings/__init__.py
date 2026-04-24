"""Arche 后端配置模块。"""

from __future__ import annotations

from .app import AppSettings
from .base import PluginSettingsBase

__all__ = [
    "AppSettings",
    "PluginSettingsBase",
]
