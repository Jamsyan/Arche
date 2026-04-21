"""OSS plugin — 文件存储插件：本地存储 + 外部写入 + 租户隔离。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry

if TYPE_CHECKING:
    from fastapi import FastAPI
    from backend.core.container import ServiceContainer

# 导入模型，确保在 create_all 前注册到 Base
from backend.plugins.oss.models import OSSFile  # noqa: F401
from backend.plugins.oss.routes import router
from backend.plugins.oss.services import StorageService


class OSSPlugin(BasePlugin):
    name = "oss"
    version = "0.1.0"
    requires = []
    optional = ["auth"]

    def setup(self, app: "FastAPI") -> None:
        """注册路由。"""
        app.include_router(router)

    def register_services(self, container: "ServiceContainer") -> None:
        """注册 StorageService 到容器。"""
        container.register("storage", lambda c: StorageService(c))

    def on_startup(self) -> None:
        pass

    def on_shutdown(self) -> None:
        pass


# 自注册
plugin = OSSPlugin()
registry.register("oss", plugin)
