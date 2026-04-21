"""OSS plugin — 文件存储插件：本地存储 + 外部写入 + 租户隔离 + 阿里云冷存储。"""

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

    def __init__(self):
        self._eviction_job = None

    def setup(self, app: "FastAPI") -> None:
        """注册路由。"""
        app.include_router(router)

    def register_services(self, container: "ServiceContainer") -> None:
        """注册 StorageService 到容器。"""
        container.register("storage", lambda c: StorageService(c))

    def on_startup(self) -> None:
        """启动冷热分层调度定时任务。"""
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.interval import IntervalTrigger

            scheduler = AsyncIOScheduler()

            async def _evict():
                storage_service = self._get_service()
                if storage_service:
                    count = await storage_service.evict_cold_files(days=7)
                    if count > 0:
                        print(f"[OSS] 冷热迁移: {count} 个文件已推到阿里云")

            scheduler.add_job(
                _evict,
                trigger=IntervalTrigger(hours=1),
                id="oss_cold_eviction",
                name="OSS 冷热分层迁移",
                replace_existing=True,
            )
            scheduler.start()
            self._eviction_job = scheduler
        except Exception:
            # APScheduler 不可用时跳过
            pass

    def on_shutdown(self) -> None:
        """关闭时停止调度器。"""
        if self._eviction_job and getattr(self._eviction_job, "running", False):
            self._eviction_job.shutdown(wait=False)

    def _get_service(self) -> StorageService | None:
        """获取 StorageService 实例。"""
        try:
            from backend.core.container import container as global_container
            return global_container.get("storage")
        except Exception:
            return None


# 自注册
plugin = OSSPlugin()
registry.register("oss", plugin)
