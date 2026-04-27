"""asset_mgmt routes integration smoke tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.tests.conftest import patch_container_service


@pytest.fixture
def asset_service_mock(db_container):
    service = MagicMock()
    service.list_assets = AsyncMock(
        return_value={"items": [{"title": "asset"}], "total": 1}
    )
    service.search_assets = AsyncMock(return_value=[{"title": "asset"}])
    service.get_stats = AsyncMock(return_value={"total_assets": 1})
    return patch_container_service(db_container, "asset_mgmt", service)


@pytest.mark.asyncio
class TestAssetMgmtAPI:
    async def test_asset_routes_require_admin(self, client, auth_headers):
        response = await client.get("/api/assets", headers=auth_headers)
        assert response.status_code == 403

    async def test_asset_catalog_search_and_stats(
        self, client, admin_headers, asset_service_mock
    ):
        listed = await client.get(
            "/api/assets",
            params={"page": 2, "page_size": 5, "asset_type": "file"},
            headers=admin_headers,
        )
        assert listed.status_code == 200
        assert listed.json()["data"]["total"] == 1
        asset_service_mock.list_assets.assert_awaited_once()

        searched = await client.get(
            "/api/assets/search",
            params={
                "keyword": "asset",
                "asset_type": "file",
                "date_from": "2024-01-01T00:00:00",
                "date_to": "2026-01-01T00:00:00",
            },
            headers=admin_headers,
        )
        assert searched.status_code == 200
        assert searched.json()["data"]["total"] == 1

        stats = await client.get("/api/assets/stats", headers=admin_headers)
        assert stats.status_code == 200
        assert stats.json()["data"]["total_assets"] == 1
