"""Crawler plugin — 网页爬虫插件：种子抓取、定时任务、结果存储。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry

if TYPE_CHECKING:
    from fastapi import FastAPI
    from backend.core.container import ServiceContainer

# 导入模型，确保在 create_all 前注册到 Base
from backend.plugins.crawler.models import CrawlTask, CrawlResult  # noqa: F401
from backend.plugins.crawler.routes import router
from backend.plugins.crawler.services import CrawlerService


class CrawlerPlugin(BasePlugin):
    name = "crawler"
    version = "0.1.0"
    requires = ["auth"]
    optional = []

    def __init__(self):
        self._scheduler = None

    def setup(self, app: "FastAPI") -> None:
        """注册路由。"""
        app.include_router(router)

    def register_services(self, container: "ServiceContainer") -> None:
        """注册 CrawlerService 到容器。"""
        container.register("crawler", lambda c: CrawlerService(c))

    def on_startup(self) -> None:
        """启动时恢复已调度的定时任务。"""
        # 延迟导入避免循环依赖
        from backend.plugins.crawler.tasks import init_scheduler

        self._scheduler = init_scheduler()

    def on_shutdown(self) -> None:
        """关闭时停止调度器。"""
        if self._scheduler and getattr(self._scheduler, "running", False):
            self._scheduler.shutdown(wait=False)


# 自注册
plugin = CrawlerPlugin()
registry.register("crawler", plugin)
