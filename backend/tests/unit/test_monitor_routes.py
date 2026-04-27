"""monitor routes 单元测试。"""

from __future__ import annotations

from fastapi import HTTPException
import pytest

from backend.plugins.monitor import routes


@pytest.mark.asyncio
class TestMonitorRoutes:
    async def test_get_session_factory_db_not_ready(self, monkeypatch):
        class _Container:
            @staticmethod
            def get(_name):
                return None

        monkeypatch.setattr("backend.core.container.container", _Container())
        with pytest.raises(HTTPException) as exc:
            routes.get_session_factory()
        assert exc.value.status_code == 500

    async def test_template_crud_and_component_data(self, in_memory_db, monkeypatch, monitor_template_payload):
        monkeypatch.setattr(routes, "get_session_factory", lambda: in_memory_db["session_factory"])

        created = await routes.create_template(routes.TemplateCreate(**monitor_template_payload))
        assert created["name"] == "CPU Dashboard"
        tid = created["id"]

        listed = await routes.list_templates()
        assert len(listed) == 1

        one = await routes.get_template(tid)
        assert one["id"] == tid

        updated = await routes.update_template(
            tid,
            routes.TemplateUpdate(name="CPU Dashboard V2", refresh_interval=20),
        )
        assert updated["name"] == "CPU Dashboard V2"
        assert updated["refresh_interval"] == 20

        comp = await routes.get_component_data("cpu")
        assert "value" in comp
        assert "timestamp" in comp

        deleted = await routes.delete_template(tid)
        assert deleted["message"] == "Template deleted"

    async def test_not_found_paths(self, in_memory_db, monkeypatch):
        monkeypatch.setattr(routes, "get_session_factory", lambda: in_memory_db["session_factory"])
        with pytest.raises(HTTPException) as exc_get:
            await routes.get_template("missing")
        assert exc_get.value.status_code == 404

        with pytest.raises(HTTPException) as exc_put:
            await routes.update_template("missing", routes.TemplateUpdate(name="x"))
        assert exc_put.value.status_code == 404

        with pytest.raises(HTTPException) as exc_del:
            await routes.delete_template("missing")
        assert exc_del.value.status_code == 404
