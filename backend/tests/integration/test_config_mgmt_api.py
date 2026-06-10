"""Config Mgmt 模块 API 集成测试。

测试真实 HTTP 请求-响应链路（HTTP → 中间件 → 真实数据库）。
config_mgmt 路由通过容器中的 config 对象访问数据库，已在 db_container
中配置 FakeConfigWithDb（带真实 session_factory），不走 mock。

覆盖：
- 列表、分组过滤、详情、更新、创建、删除
- 敏感值掩码
- 鉴权失败（403）边界
- 404 边界
"""

from __future__ import annotations

import pytest

from backend.core.models import ConfigEntry


@pytest.fixture
async def config_entries(in_memory_db):
    """预置测试用配置数据。"""
    async with in_memory_db["session_factory"]() as session:
        session.add_all(
            [
                ConfigEntry(
                    key="PUBLIC_NAME",
                    value="Arche",
                    group="app",
                    description="public setting",
                    is_sensitive=False,
                ),
                ConfigEntry(
                    key="SECRET_TOKEN",
                    value="token-value",
                    group="secrets",
                    description="secret setting",
                    is_sensitive=True,
                ),
                ConfigEntry(
                    key="MAX_ITEMS",
                    value="100",
                    group="app",
                    description="max items",
                    is_sensitive=False,
                ),
            ]
        )
        await session.commit()


@pytest.mark.asyncio
class TestConfigMgmtAPI:
    """配置管理接口测试。"""

    async def test_config_requires_admin(self, client, auth_headers):
        """普通用户无法访问配置管理接口。"""
        response = await client.get("/api/admin/config", headers=auth_headers)
        assert response.status_code == 403

    async def test_list_configs(self, client, admin_headers, config_entries):
        """列出所有配置，敏感值应掩码。"""
        listed = await client.get("/api/admin/config", headers=admin_headers)
        assert listed.status_code == 200
        values = {item["key"]: item["value"] for item in listed.json()["data"]}
        assert values["PUBLIC_NAME"] == "Arche"
        assert values["SECRET_TOKEN"] == "***"
        assert values["MAX_ITEMS"] == "100"

    async def test_filter_by_group(self, client, admin_headers, config_entries):
        """按分组过滤配置。"""
        grouped = await client.get(
            "/api/admin/config",
            params={"group": "app"},
            headers=admin_headers,
        )
        keys = [item["key"] for item in grouped.json()["data"]]
        assert "PUBLIC_NAME" in keys
        assert "MAX_ITEMS" in keys
        assert "SECRET_TOKEN" not in keys

    async def test_get_single_config(self, client, admin_headers, config_entries):
        """获取单条配置详情，敏感字段返回真实值。"""
        detail = await client.get(
            "/api/admin/config/SECRET_TOKEN", headers=admin_headers
        )
        assert detail.status_code == 200
        assert detail.json()["data"]["value"] == "token-value"

    async def test_update_config(self, client, admin_headers, config_entries):
        """更新配置值，验证持久化。"""
        updated = await client.put(
            "/api/admin/config/PUBLIC_NAME",
            json={"value": "Arche Next"},
            headers=admin_headers,
        )
        assert updated.status_code == 200

        # 验证已更新
        detail = await client.get(
            "/api/admin/config/PUBLIC_NAME", headers=admin_headers
        )
        assert detail.json()["data"]["value"] == "Arche Next"

    async def test_create_and_delete_config(self, client, admin_headers):
        """新建配置，然后删除。"""
        # 创建
        created = await client.post(
            "/api/admin/config",
            json={
                "key": "MY_CUSTOM_KEY",
                "value": "custom_value",
                "group": "custom",
                "description": "a custom config",
                "is_sensitive": False,
            },
            headers=admin_headers,
        )
        assert created.status_code == 200
        assert created.json()["data"]["key"] == "MY_CUSTOM_KEY"

        # 验证存在
        detail = await client.get(
            "/api/admin/config/MY_CUSTOM_KEY", headers=admin_headers
        )
        assert detail.status_code == 200

        # 删除
        deleted = await client.delete(
            "/api/admin/config/MY_CUSTOM_KEY", headers=admin_headers
        )
        assert deleted.status_code == 200

        # 验证已删除
        after = await client.get(
            "/api/admin/config/MY_CUSTOM_KEY", headers=admin_headers
        )
        assert after.json()["code"] == "error"

    async def test_get_non_existent_config_returns_error(self, client, admin_headers):
        """不存在的配置项返回 error。"""
        missing = await client.get(
            "/api/admin/config/UNKNOWN_KEY", headers=admin_headers
        )
        assert missing.status_code == 200
        assert missing.json()["code"] == "error"

    async def test_reload_config(self, client, admin_headers, config_entries):
        """重载配置缓存成功。"""
        reloaded = await client.post(
            "/api/admin/config/reload", headers=admin_headers
        )
        assert reloaded.status_code == 200
        assert reloaded.json()["code"] == "ok"
