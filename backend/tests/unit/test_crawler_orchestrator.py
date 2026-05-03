"""CrawlerOrchestrator 单元测试。"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.plugins.crawler.models import CrawlRecord
from backend.plugins.crawler.pipeline import CrawlItem
from backend.plugins.crawler.services import CrawlerOrchestrator


class _ProbeOk:
    async def probe(self, url: str):
        return {
            "url": url,
            "status_code": 200,
            "has_content": True,
            "is_functional": False,
        }

    async def close(self):
        return None


class _ProbeFunctional:
    async def probe(self, url: str):
        return {
            "url": url,
            "status_code": 200,
            "has_content": True,
            "is_functional": True,
        }

    async def close(self):
        return None


@pytest.mark.asyncio
class TestCrawlerOrchestrator:
    async def test_add_seed_delegates_to_seed_manager(self):
        container = MagicMock()
        orch = CrawlerOrchestrator(container)
        orch.seed_manager = MagicMock()
        orch.seed_manager.add_seed.return_value = True
        result = await orch.add_seed("https://example.com")
        assert result is True
        orch.seed_manager.add_seed.assert_called_once()

    async def test_get_status_includes_runtime_counters(self):
        container = MagicMock()
        orch = CrawlerOrchestrator(container)
        orch._running = True
        orch._start_time = time.monotonic() - 5
        orch._pages_crawled = 3
        orch._pages_rejected = 2
        orch.url_scheduler = MagicMock()
        orch.url_scheduler.active_count = 1
        orch.url_scheduler.queue_size = 4
        orch.url_scheduler.domains_active = {"example.com": 1}
        orch.seed_manager = MagicMock()
        orch.seed_manager.queue_size = 2
        status = await orch.get_status()
        assert status["running"] is True
        assert status["pages_crawled"] == 3
        assert status["pages_rejected"] == 2
        assert status["queue_size"] == 6

    async def test_run_pipeline_rejects_functional_page(self, monkeypatch):
        container = MagicMock()
        orch = CrawlerOrchestrator(container)
        monkeypatch.setattr(
            "backend.plugins.crawler.probe.ProbeService", _ProbeFunctional
        )
        orch.seed_manager = MagicMock()
        orch.url_scheduler = AsyncMock()
        result = await orch._run_pipeline("https://example.com/login")
        assert result is None
        assert orch._pages_rejected == 1
        orch.seed_manager.add_to_blacklist.assert_called_once()

    async def test_run_pipeline_success_path(self, monkeypatch):
        container = MagicMock()
        orch = CrawlerOrchestrator(container)
        monkeypatch.setattr("backend.plugins.crawler.probe.ProbeService", _ProbeOk)
        orch.url_scheduler = AsyncMock()
        orch.seed_manager = MagicMock()
        orch._save_record = MagicMock()

        item = CrawlItem(
            url="https://example.com/article/1",
            title="T",
            content="x" * 100,
            links=["https://example.com/next"],
            quality_passed=True,
        )
        orch.fetch_stage = AsyncMock()
        orch.parse_stage = AsyncMock()
        orch.classify_stage = AsyncMock()
        orch.quality_stage = AsyncMock()
        orch.storage_stage = AsyncMock()
        orch.fetch_stage.process = AsyncMock(return_value=item)
        orch.parse_stage.process = AsyncMock(return_value=item)
        orch.classify_stage.process = AsyncMock(return_value=item)
        orch.quality_stage.process = AsyncMock(return_value=item)
        orch.storage_stage.process = AsyncMock(return_value=item)

        result = await orch._run_pipeline(item.url)
        assert result is item
        assert orch._pages_crawled == 1
        orch.seed_manager.discover_seeds_from_links.assert_called_once()
        orch._save_record.assert_called_once_with(item)
        orch.url_scheduler.acquire.assert_awaited_once()
        orch.url_scheduler.release.assert_awaited_once()

    async def test_run_pipeline_probe_exception_rejected(self, monkeypatch):
        class _ProbeError:
            async def probe(self, _url):
                raise RuntimeError("boom")

            async def close(self):
                return None

        container = MagicMock()
        orch = CrawlerOrchestrator(container)
        monkeypatch.setattr("backend.plugins.crawler.probe.ProbeService", _ProbeError)
        orch.url_scheduler = AsyncMock()
        result = await orch._run_pipeline("https://example.com/x")
        assert result is None
        assert orch._pages_rejected == 1
        orch.url_scheduler.acquire.assert_not_called()

    async def test_run_pipeline_quality_or_storage_failed(self, monkeypatch):
        container = MagicMock()
        orch = CrawlerOrchestrator(container)
        monkeypatch.setattr("backend.plugins.crawler.probe.ProbeService", _ProbeOk)
        orch.url_scheduler = AsyncMock()
        orch.seed_manager = MagicMock()

        item = CrawlItem(
            url="https://example.com/x",
            content="x" * 100,
            quality_passed=True,
        )
        orch.fetch_stage = AsyncMock()
        orch.parse_stage = AsyncMock()
        orch.classify_stage = AsyncMock()
        orch.quality_stage = AsyncMock()
        orch.storage_stage = AsyncMock()
        orch.fetch_stage.process = AsyncMock(return_value=item)
        orch.parse_stage.process = AsyncMock(return_value=item)
        orch.classify_stage.process = AsyncMock(return_value=item)
        orch.quality_stage.process = AsyncMock(return_value=item)
        orch.storage_stage.process = AsyncMock(return_value=None)

        result = await orch._run_pipeline(item.url)
        assert result is None
        assert orch._pages_rejected == 1

    async def test_get_recent_record_and_stats_from_db(self, db_container):
        orch = CrawlerOrchestrator(db_container)
        db = db_container.get("db")
        async with db["session_factory"]() as session:
            rec = CrawlRecord(
                id=uuid.uuid4(),
                url="https://example.com/a",
                title="A",
                content_type="article",
                status_code=200,
                source="example.com",
                crawled_at=datetime.now(timezone.utc),
                file_path="example/a.json",
                file_size=10,
            )
            session.add(rec)
            await session.commit()
            rec_id = str(rec.id)

        recent = await orch.get_recent_records(limit=10)
        assert len(recent) == 1
        one = await orch.get_record(rec_id)
        assert one is not None
        assert one["url"] == "https://example.com/a"
        stats = await orch.get_stats()
        assert stats["total_crawled"] == 1
        assert stats["by_type"]["article"] == 1

    async def test_get_record_returns_none_for_missing(self, db_container):
        orch = CrawlerOrchestrator(db_container)
        missing = await orch.get_record(str(uuid.uuid4()))
        assert missing is None
