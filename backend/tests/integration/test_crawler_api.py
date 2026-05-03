"""Crawler API 集成测试。"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.tests.conftest import patch_container_service


@pytest.fixture
def crawler_mock(db_container):
    orchestrator = MagicMock()
    orchestrator.get_status = AsyncMock(
        return_value={"running": True, "pages_crawled": 1, "pages_rejected": 0}
    )
    orchestrator.start = AsyncMock()
    orchestrator.stop = AsyncMock()
    orchestrator.get_recent_records = AsyncMock(return_value=[])
    orchestrator.get_record = AsyncMock(return_value=None)
    orchestrator.get_stats = AsyncMock(return_value={"total_crawled": 0})
    orchestrator.add_seed = AsyncMock(return_value=True)
    orchestrator.seed_manager = MagicMock()
    orchestrator.seed_manager.queue_size = 1
    orchestrator.seed_manager.total_seen = 2
    orchestrator.seed_manager.get_blacklist.return_value = ["bad.com"]
    orchestrator.seed_manager.get_whitelist.return_value = ["good.com"]
    orchestrator.seed_manager.add_to_blacklist = MagicMock()
    return patch_container_service(db_container, "crawler", orchestrator)


@pytest.mark.asyncio
class TestCrawlerAPI:
    async def test_status_start_stop(self, client, admin_headers, crawler_mock):
        status = await client.get("/api/crawler/status", headers=admin_headers)
        assert status.status_code == 200
        assert status.json()["code"] == "ok"

        started = await client.post("/api/crawler/start", headers=admin_headers)
        assert started.status_code == 200
        crawler_mock.start.assert_awaited_once()

        stopped = await client.post("/api/crawler/stop", headers=admin_headers)
        assert stopped.status_code == 200
        crawler_mock.stop.assert_awaited_once()

    async def test_seeds_and_blacklist_endpoints(
        self, client, admin_headers, crawler_mock
    ):
        add_seed = await client.post(
            "/api/crawler/seeds",
            headers=admin_headers,
            json={"url": "https://example.com/article/1"},
        )
        assert add_seed.status_code == 200
        assert add_seed.json()["code"] == "ok"

        seeds = await client.get("/api/crawler/seeds", headers=admin_headers)
        assert seeds.status_code == 200
        assert seeds.json()["data"]["queue_size"] == 1
        assert seeds.json()["data"]["blacklist"] == ["bad.com"]

        add_black = await client.post(
            "/api/crawler/blacklist",
            headers=admin_headers,
            json={"pattern": "spam.com", "reason": "spam"},
        )
        assert add_black.status_code == 200
        crawler_mock.seed_manager.add_to_blacklist.assert_called_once_with(
            "spam.com", "spam"
        )

        get_black = await client.get("/api/crawler/blacklist", headers=admin_headers)
        assert get_black.status_code == 200
        assert get_black.json()["code"] == "ok"

    async def test_records_stats_and_not_found(
        self, client, admin_headers, crawler_mock
    ):
        crawler_mock.get_recent_records.return_value = [
            {"id": "1", "url": "https://a.com"},
            {"id": "2", "url": "https://b.com"},
        ]
        records = await client.get(
            "/api/crawler/records?page=1&page_size=1", headers=admin_headers
        )
        assert records.status_code == 200
        assert records.json()["data"]["total"] == 2
        assert len(records.json()["data"]["items"]) == 1

        missing = await client.get(
            "/api/crawler/records/not-found", headers=admin_headers
        )
        assert missing.status_code == 200
        assert missing.json()["code"] == "not_found"

        stats = await client.get("/api/crawler/stats", headers=admin_headers)
        assert stats.status_code == 200
        assert stats.json()["code"] == "ok"

    async def test_record_file_found_and_missing(
        self, client, admin_headers, crawler_mock, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("CRAWLER_STORAGE_ROOT", str(tmp_path))
        file_path = tmp_path / "example" / "record.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps({"ok": True}), encoding="utf-8")
        crawler_mock.get_record.return_value = {
            "id": "x",
            "file_path": "example/record.json",
        }

        found = await client.get("/api/crawler/records/abc/file", headers=admin_headers)
        assert found.status_code == 200
        assert found.json()["code"] == "ok"
        assert found.json()["data"]["ok"] is True

        crawler_mock.get_record.return_value = {"id": "x", "file_path": "missing.json"}
        missing = await client.get(
            "/api/crawler/records/abc/file", headers=admin_headers
        )
        assert missing.status_code == 200
        assert missing.json()["code"] == "not_found"

    async def test_requires_auth(self, client, crawler_mock):
        response = await client.get("/api/crawler/status")
        assert response.status_code == 401
