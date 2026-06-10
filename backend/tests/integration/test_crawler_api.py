"""爬虫全链路集成测试。

爬虫插件依赖的外部 HTTP 抓取（FetchStage + ProbeService 中的 httpx.AsyncClient）
仅在实际运行爬虫循环时才会被调用。本测试仅测试 API 路由层的控制和管理功能
（状态/启停/种子/记录），不触发实际爬取，因此无需 mock 任何外部依赖。

Mock 边界：无（所有操作都是内存操作或真实 DB 查询）。
不 mock CrawlerOrchestrator 或其任何内部服务。
"""

from __future__ import annotations

import json

import pytest

from backend.plugins.crawler.models import CrawlRecord
from backend.plugins.crawler.services import CrawlerOrchestrator
from backend.tests.conftest import patch_container_service


@pytest.fixture
def crawler_service(db_container):
    """使用真实 CrawlerOrchestrator 注入容器。"""
    svc = CrawlerOrchestrator(db_container)
    patch_container_service(db_container, "crawler", svc)
    return svc


@pytest.mark.asyncio
class TestCrawlerAPI:
    """爬虫 API 全链路集成测试。"""

    async def test_unauthenticated_returns_401(self, client):
        """未登录访问爬虫接口应返回 401。"""
        response = await client.get("/api/crawler/status")
        assert response.status_code == 401

    async def test_status_start_stop(self, client, admin_headers, crawler_service):
        """爬虫状态查询、启动、停止全流程。"""
        status1 = await client.get("/api/crawler/status", headers=admin_headers)
        assert status1.status_code == 200
        assert status1.json()["code"] == "ok"

        started = await client.post("/api/crawler/start", headers=admin_headers)
        assert started.status_code == 200
        assert started.json()["code"] == "ok"

        status2 = await client.get("/api/crawler/status", headers=admin_headers)
        assert status2.status_code == 200

        stopped = await client.post("/api/crawler/stop", headers=admin_headers)
        assert stopped.status_code == 200
        assert stopped.json()["code"] == "ok"

    async def test_seed_management(self, client, admin_headers, crawler_service):
        """添加种子、查询种子和黑名单。"""
        add_seed = await client.post(
            "/api/crawler/seeds",
            headers=admin_headers,
            json={"url": "https://example.com/article/1"},
        )
        assert add_seed.status_code == 200
        assert add_seed.json()["code"] == "ok"

        seeds = await client.get("/api/crawler/seeds", headers=admin_headers)
        assert seeds.status_code == 200
        data = seeds.json()["data"]
        assert data["queue_size"] >= 1

        add_black = await client.post(
            "/api/crawler/blacklist",
            headers=admin_headers,
            json={"pattern": "spam.com", "reason": "spam"},
        )
        assert add_black.status_code == 200
        assert add_black.json()["code"] == "ok"

        get_black = await client.get("/api/crawler/blacklist", headers=admin_headers)
        assert get_black.status_code == 200
        assert "spam.com" in get_black.json()["data"]

    async def test_record_query(self, client, admin_headers, crawler_service):
        """查询爬取记录和统计（空数据库场景）。"""
        records = await client.get("/api/crawler/records", headers=admin_headers)
        assert records.status_code == 200
        data = records.json()["data"]
        assert data["total"] == 0
        assert data["items"] == []

        stats = await client.get("/api/crawler/stats", headers=admin_headers)
        assert stats.status_code == 200
        assert stats.json()["code"] == "ok"

    async def test_record_file_read(
        self, client, admin_headers, db_container, tmp_path, monkeypatch
    ):
        """通过 crawler 记录的文件路径读取文件内容。"""
        monkeypatch.setenv("CRAWLER_STORAGE_ROOT", str(tmp_path))

        db = db_container.get("db")
        session_factory = db["session_factory"]

        # 插入记录
        async with session_factory() as session:
            record = CrawlRecord(
                url="https://example.com/article/test",
                source="example.com",
                title="Test Article",
                file_path="test_record.json",
            )
            session.add(record)
            await session.commit()
            record_id = str(record.id)

        # 创建文件
        file_path = tmp_path / "test_record.json"
        file_path.write_text(json.dumps({"content": "hello world"}), encoding="utf-8")

        # 注入真实 orchestrator
        orchestrator = CrawlerOrchestrator(db_container)
        patch_container_service(db_container, "crawler", orchestrator)

        # 读取存在的记录文件
        found = await client.get(
            f"/api/crawler/records/{record_id}/file", headers=admin_headers
        )
        assert found.status_code == 200
        assert found.json()["code"] == "ok"
        assert found.json()["data"]["content"] == "hello world"

        # 不存在的记录（使用合法 UUID 格式）
        fake_id = "00000000-0000-0000-0000-000000000000"
        missing = await client.get(
            f"/api/crawler/records/{fake_id}/file", headers=admin_headers
        )
        assert missing.status_code == 200
        assert missing.json()["code"] == "not_found"

    async def test_快速统计(self, client, admin_headers, crawler_service):
        """/api/crawler/stats 应返回统计信息。"""
        stats = await client.get("/api/crawler/stats", headers=admin_headers)
        assert stats.status_code == 200
        assert stats.json()["code"] == "ok"
