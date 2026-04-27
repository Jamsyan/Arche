"""monitor models 单元测试。"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.plugins.monitor.models import MonitorTemplate


class TestMonitorTemplate:
    def test_to_dict_defaults_and_timestamps(self):
        now = datetime.now(timezone.utc)
        tpl = MonitorTemplate(
            id="t1",
            name="Main",
            user_id=None,
            components=None,
            refresh_interval=30,
            created_at=now,
            updated_at=now,
        )
        data = tpl.to_dict()
        assert data["id"] == "t1"
        assert data["name"] == "Main"
        assert data["components"] == []
        assert data["refresh_interval"] == 30
        assert data["created_at"] is not None
        assert data["updated_at"] is not None
