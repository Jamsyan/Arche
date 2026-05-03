"""config_mgmt routes integration tests."""

from __future__ import annotations

import pytest

from backend.core.models import ConfigEntry


@pytest.fixture
async def config_entries(in_memory_db):
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
            ]
        )
        await session.commit()


@pytest.mark.asyncio
class TestConfigMgmtAPI:
    async def test_config_requires_admin(self, client, auth_headers):
        response = await client.get("/api/admin/config", headers=auth_headers)
        assert response.status_code == 403

    async def test_list_get_update_and_reload_config(
        self, client, admin_headers, config_entries
    ):
        listed = await client.get("/api/admin/config", headers=admin_headers)
        assert listed.status_code == 200
        values = {item["key"]: item["value"] for item in listed.json()["data"]}
        assert values["PUBLIC_NAME"] == "Arche"
        assert values["SECRET_TOKEN"] == "***"

        grouped = await client.get(
            "/api/admin/config",
            params={"group": "app"},
            headers=admin_headers,
        )
        assert [item["key"] for item in grouped.json()["data"]] == ["PUBLIC_NAME"]

        detail = await client.get(
            "/api/admin/config/SECRET_TOKEN", headers=admin_headers
        )
        assert detail.status_code == 200
        assert detail.json()["data"]["value"] == "token-value"

        updated = await client.put(
            "/api/admin/config/PUBLIC_NAME",
            json={"value": "Arche Next"},
            headers=admin_headers,
        )
        assert updated.status_code == 200

        detail = await client.get(
            "/api/admin/config/PUBLIC_NAME", headers=admin_headers
        )
        assert detail.json()["data"]["value"] == "Arche Next"

        missing = await client.get("/api/admin/config/UNKNOWN", headers=admin_headers)
        assert missing.status_code == 200
        assert missing.json()["code"] == "error"

        reloaded = await client.post("/api/admin/config/reload", headers=admin_headers)
        assert reloaded.status_code == 200
        assert reloaded.json()["code"] == "ok"
