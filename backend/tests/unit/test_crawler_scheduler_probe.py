"""UrlScheduler 与 ProbeService 单元测试。"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend.plugins.crawler.probe import ProbeService
from backend.plugins.crawler.url_scheduler import UrlScheduler


class _ProbeResponse:
    def __init__(
        self,
        url: str,
        text: str,
        status_code: int = 200,
        content_type: str = "text/html",
    ):
        self.url = url
        self.text = text
        self.status_code = status_code
        self.headers = {"content-type": content_type}


@pytest.mark.asyncio
class TestUrlScheduler:
    async def test_enqueue_dequeue_and_size(self):
        scheduler = UrlScheduler(max_global=2, max_per_domain=1)
        await scheduler.enqueue("https://a.com/1")
        await scheduler.enqueue("https://b.com/2")
        assert scheduler.queue_size == 2
        assert await scheduler.dequeue() == "https://a.com/1"
        assert await scheduler.dequeue() == "https://b.com/2"
        assert await scheduler.dequeue() is None

    async def test_domain_limit_blocks_dequeue(self):
        scheduler = UrlScheduler(max_global=2, max_per_domain=1)
        await scheduler.enqueue("https://a.com/1")
        await scheduler.enqueue("https://a.com/2")
        await scheduler.acquire("https://a.com/running")
        try:
            assert await scheduler.dequeue() is None
        finally:
            await scheduler.release("https://a.com/running")

    async def test_acquire_release_updates_active_counters(self):
        scheduler = UrlScheduler(max_global=2, max_per_domain=1)
        await scheduler.acquire("https://x.com/1")
        assert scheduler.active_count == 1
        assert scheduler.domains_active["x.com"] == 1
        await scheduler.release("https://x.com/1")
        assert scheduler.active_count == 0
        assert scheduler.domains_active["x.com"] == 0

    async def test_can_fetch_respects_domain_limit(self):
        scheduler = UrlScheduler(max_global=2, max_per_domain=1)
        assert await scheduler.can_fetch("https://x.com/1") is True
        await scheduler.acquire("https://x.com/1")
        try:
            assert await scheduler.can_fetch("https://x.com/2") is False
        finally:
            await scheduler.release("https://x.com/1")


@pytest.mark.asyncio
class TestProbeService:
    async def test_probe_detects_functional_by_path(self, monkeypatch):
        service = ProbeService()
        fake_client = AsyncMock()
        fake_client.get = AsyncMock(
            return_value=_ProbeResponse(
                "https://example.com/login",
                "<html><title>Welcome</title><body>" + ("x" * 200) + "</body></html>",
            )
        )
        monkeypatch.setattr(service, "_get_client", AsyncMock(return_value=fake_client))
        result = await service.probe("https://example.com/login")
        assert result["is_functional"] is True
        assert result["has_content"] is True

    async def test_probe_detects_functional_by_title(self, monkeypatch):
        service = ProbeService()
        fake_client = AsyncMock()
        fake_client.get = AsyncMock(
            return_value=_ProbeResponse(
                "https://example.com/home",
                "<html><title>Sign In</title><body>" + ("x" * 200) + "</body></html>",
            )
        )
        monkeypatch.setattr(service, "_get_client", AsyncMock(return_value=fake_client))
        result = await service.probe("https://example.com/home")
        assert result["is_functional"] is True

    async def test_probe_returns_fallback_on_exception(self, monkeypatch):
        service = ProbeService()
        fake_client = AsyncMock()
        fake_client.get = AsyncMock(side_effect=RuntimeError("net down"))
        monkeypatch.setattr(service, "_get_client", AsyncMock(return_value=fake_client))
        result = await service.probe("https://example.com/x")
        assert result["status_code"] == 0
        assert result["has_content"] is False

    async def test_probe_skips_non_html_response(self, monkeypatch):
        service = ProbeService()
        fake_client = AsyncMock()
        fake_client.get = AsyncMock(
            return_value=_ProbeResponse(
                "https://example.com/file.pdf",
                "%PDF",
                content_type="application/pdf",
            )
        )
        monkeypatch.setattr(service, "_get_client", AsyncMock(return_value=fake_client))
        result = await service.probe("https://example.com/file.pdf")
        assert result["content_type"] == "application/pdf"
        assert result["has_content"] is False

    async def test_probe_skips_large_response_by_header(self, monkeypatch):
        service = ProbeService()
        fake_client = AsyncMock()
        response = _ProbeResponse(
            "https://example.com/large",
            "<html></html>",
            content_type="text/html",
        )
        response.headers["content-length"] = str(1024 * 1024)
        fake_client.get = AsyncMock(return_value=response)
        monkeypatch.setattr(service, "_get_client", AsyncMock(return_value=fake_client))
        result = await service.probe("https://example.com/large")
        assert result["has_content"] is False

    async def test_close_resets_client(self):
        service = ProbeService()
        service._client = AsyncMock()
        await service.close()
        assert service._client is None
