"""monitor API 最小烟囱集成测试。"""

from __future__ import annotations

import pytest

from backend.core.container import container as global_container


@pytest.fixture
def monitor_global_db(in_memory_db):
    """把内存 DB 注册到全局 container，并在测试结束后还原快照。

    monitor 路由通过 `backend.core.container.container` 拿 db，所以
    集成测试需要写入全局 container；为避免污染同进程后续用例，这里
    在 yield 后恢复 _factories 与 _instances 的原始状态。
    """
    factories_snapshot = dict(global_container._factories)
    instances_snapshot = dict(global_container._instances)

    global_container._instances.pop("db", None)
    global_container.register("db", lambda _c: in_memory_db)

    try:
        yield in_memory_db
    finally:
        global_container._factories.clear()
        global_container._factories.update(factories_snapshot)
        global_container._instances.clear()
        global_container._instances.update(instances_snapshot)


@pytest.mark.asyncio
class TestMonitorAPI:
    async def test_monitor_template_crud_http(self, client, admin_headers, monitor_template_payload, monitor_global_db):
        created = await client.post(
            "/api/monitor/templates",
            json=monitor_template_payload,
            headers=admin_headers,
        )
        assert created.status_code == 200
        data = created.json()
        assert data["name"] == monitor_template_payload["name"]
        tid = data["id"]

        listed = await client.get("/api/monitor/templates", headers=admin_headers)
        assert listed.status_code == 200
        assert len(listed.json()) >= 1

        one = await client.get(f"/api/monitor/templates/{tid}", headers=admin_headers)
        assert one.status_code == 200
        assert one.json()["id"] == tid

        updated = await client.put(
            f"/api/monitor/templates/{tid}",
            json={"name": "Updated Monitor", "refresh_interval": 10},
            headers=admin_headers,
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Updated Monitor"

        deleted = await client.delete(f"/api/monitor/templates/{tid}", headers=admin_headers)
        assert deleted.status_code == 200
        assert deleted.json()["message"] == "Template deleted"

    async def test_monitor_not_found_http(self, client, admin_headers, monitor_global_db):
        resp = await client.get("/api/monitor/templates/not-exist", headers=admin_headers)
        assert resp.status_code == 404
