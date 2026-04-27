"""monitor 插件初始化测试。"""

from __future__ import annotations

from fastapi import FastAPI

from backend.plugins.monitor import MonitorPlugin


class TestMonitorPlugin:
    def test_setup_registers_routes(self):
        app = FastAPI()
        plugin = MonitorPlugin()
        plugin.setup(app)
        paths = {route.path for route in app.routes}
        assert "/api/monitor/templates" in paths
        assert "/api/monitor/components/{component_id}/data" in paths

    def test_register_services_noop(self):
        plugin = MonitorPlugin()
        plugin.register_services(container=None)
