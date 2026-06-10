"""Monitor 模块 API 集成测试。

测试真实 HTTP 请求-响应链路（HTTP → 中间件 → 真实数据库）。
monitor 路由通过全局容器访问数据库，使用 monitor_global_db fixture
将全局容器的 DB 指向同一内存数据库。

覆盖：
- 监控模板 CRUD（创建 → 列表 → 详情 → 更新 → 删除）
- 404 边界
- 鉴权失败（403）边界
"""

from __future__ import annotations

import pytest

from backend.core.container import container as global_container


@pytest.fixture
def monitor_global_db(in_memory_db):
    """把内存 DB 注册到全局 container，供 monitor 路由使用。"""
    factories_snapshot = dict(global_container._factories)
    instances_snapshot = dict(global_container._instances)

    global_container._instances.pop("db", None)

    def _db_factory(_c):
        return in_memory_db

    global_container.register("db", _db_factory)

    try:
        yield in_memory_db
    finally:
        global_container._factories.clear()
        global_container._factories.update(factories_snapshot)
        global_container._instances.clear()
        global_container._instances.update(instances_snapshot)


@pytest.mark.asyncio
class TestMonitorAPI:
    """监控模板 CRUD 测试。"""

    async def test_templates_require_admin(self, client, auth_headers, monitor_global_db):
        """普通用户无法访问监控模板接口。"""
        response = await client.get("/api/monitor/templates", headers=auth_headers)
        assert response.status_code == 403

    async def test_template_crud(self, client, admin_headers, monitor_global_db):
        """完整的模板 CRUD 流程。"""
        # 创建
        payload = {
            "name": "CPU Dashboard",
            "components": [{"id": "cpu", "type": "metric"}],
            "refresh_interval": 15,
        }
        created = await client.post(
            "/api/monitor/templates",
            json=payload,
            headers=admin_headers,
        )
        assert created.status_code == 200
        data = created.json()
        assert data["name"] == payload["name"]
        assert data["refresh_interval"] == 15
        tid = data["id"]

        # 列表
        listed = await client.get("/api/monitor/templates", headers=admin_headers)
        assert listed.status_code == 200
        assert len(listed.json()) >= 1
        tids = [t["id"] for t in listed.json()]
        assert tid in tids

        # 详情
        detail = await client.get(
            f"/api/monitor/templates/{tid}", headers=admin_headers
        )
        assert detail.status_code == 200
        assert detail.json()["id"] == tid
        assert detail.json()["name"] == payload["name"]

        # 更新
        updated = await client.put(
            f"/api/monitor/templates/{tid}",
            json={"name": "Updated Monitor", "refresh_interval": 10},
            headers=admin_headers,
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Updated Monitor"
        assert updated.json()["refresh_interval"] == 10

        # 删除
        deleted = await client.delete(
            f"/api/monitor/templates/{tid}", headers=admin_headers
        )
        assert deleted.status_code == 200
        assert deleted.json()["message"] == "Template deleted"

        # 验证已删除
        get_deleted = await client.get(
            f"/api/monitor/templates/{tid}", headers=admin_headers
        )
        assert get_deleted.status_code == 404

    async def test_get_non_existent_template_returns_404(
        self, client, admin_headers, monitor_global_db
    ):
        """获取不存在的模板返回 404。"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.get(
            f"/api/monitor/templates/{fake_id}", headers=admin_headers
        )
        assert resp.status_code == 404

    async def test_update_non_existent_template_returns_404(
        self, client, admin_headers, monitor_global_db
    ):
        """更新不存在的模板返回 404。"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.put(
            f"/api/monitor/templates/{fake_id}",
            json={"name": "Nope"},
            headers=admin_headers,
        )
        assert resp.status_code == 404

    async def test_delete_non_existent_template_returns_404(
        self, client, admin_headers, monitor_global_db
    ):
        """删除不存在的模板返回 404。"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.delete(
            f"/api/monitor/templates/{fake_id}", headers=admin_headers
        )
        assert resp.status_code == 404
