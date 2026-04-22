"""Crawler plugin — 漫游爬虫插件：24 小时常驻后台服务，纯 HTTP 请求。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry

if TYPE_CHECKING:
    from fastapi import FastAPI
    from backend.core.container import ServiceContainer

# 导入模型，确保在 create_all 前注册到 Base
from backend.plugins.crawler.models import CrawlRecord  # noqa: F401
from backend.plugins.crawler.routes import router
from backend.plugins.crawler.services import CrawlerOrchestrator


class CrawlerPlugin(BasePlugin):
    name = "crawler"
    version = "0.2.0"
    requires = ["auth"]
    optional = ["oss"]

    def setup(self, app: "FastAPI") -> None:
        """注册路由。"""
        app.include_router(router)

    def register_services(self, container: "ServiceContainer") -> None:
        """注册 CrawlerOrchestrator 到容器。"""
        container.register("crawler", lambda c: CrawlerOrchestrator(c))

    def on_startup(self) -> None:
        """启动时初始化并启动常驻守护进程。"""
        import asyncio
        from backend.core.container import container as global_container

        orchestrator = global_container.get("crawler")
        if orchestrator:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(orchestrator.start())
            except RuntimeError:
                pass

    def on_shutdown(self) -> None:
        """关闭时停止爬虫。"""
        import asyncio
        from backend.core.container import container as global_container

        orchestrator = global_container.get("crawler")
        if orchestrator:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(orchestrator.stop())
            except RuntimeError:
                pass


# 自注册
plugin = CrawlerPlugin()
registry.register("crawler", plugin)
