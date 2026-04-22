"""System Monitor plugin — 系统资源监控插件。

采集 CPU/内存/磁盘/网络等系统指标，APScheduler 定时采样，内存循环缓冲。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry

if TYPE_CHECKING:
    from fastapi import FastAPI
    from backend.core.container import ServiceContainer

from backend.plugins.system_monitor.routes import router
from backend.plugins.system_monitor.services import SystemMonitorService


class SystemMonitorPlugin(BasePlugin):
    name = "system_monitor"
    version = "0.1.0"
    requires = ["auth"]
    optional = []

    def __init__(self):
        self._app = None

    def setup(self, app: "FastAPI") -> None:
        self._app = app
        app.include_router(router)

    def register_services(self, container: "ServiceContainer") -> None:
        container.register("system_monitor", lambda c: SystemMonitorService(c))

    def on_startup(self) -> None:
        import asyncio
        from backend.core.plugin_registry import registry as _reg

        async def _start():
            container = _reg.container
            if "system_monitor" in container._factories:
                svc = container.get("system_monitor")
                svc.start_collection()

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(_start())
            else:
                loop.run_until_complete(_start())
        except Exception:
            pass

    def on_shutdown(self) -> None:
        try:
            from backend.core.container import container as gc
            if gc.is_available("system_monitor"):
                svc = gc.get("system_monitor")
                svc.stop_collection()
        except Exception:
            pass


plugin = SystemMonitorPlugin()
registry.register("system_monitor", plugin)
