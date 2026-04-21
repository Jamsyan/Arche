"""Cloud Integration plugin — 云训练插件。

负责 ML 模型训练任务的管理：创建、启动、停止、监控。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry

if TYPE_CHECKING:
    from fastapi import FastAPI
    from backend.core.container import ServiceContainer

# 导入模型，确保在 create_all 前注册到 Base
from backend.plugins.cloud_integration.models import TrainingJob, TrainingInstance  # noqa: F401
from backend.plugins.cloud_integration.routes import router
from backend.plugins.cloud_integration.services import CloudTrainingService


class CloudIntegrationPlugin(BasePlugin):
    name = "cloud_integration"
    version = "0.1.0"
    requires = ["auth"]
    optional = []

    def __init__(self):
        self._app = None

    def setup(self, app: "FastAPI") -> None:
        """注册路由。"""
        self._app = app
        app.include_router(router)

    def register_services(self, container: "ServiceContainer") -> None:
        """注册 CloudTrainingService 到容器。"""
        container.register("cloud_training", lambda c: CloudTrainingService(c))

    def on_startup(self) -> None:
        pass

    def on_shutdown(self) -> None:
        pass


# 自注册
plugin = CloudIntegrationPlugin()
registry.register("cloud_integration", plugin)
