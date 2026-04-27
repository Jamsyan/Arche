"""Crawler pipeline 相关单元测试。"""

from __future__ import annotations

import gzip
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.plugins.crawler.link_extractor import extract_links
from backend.plugins.crawler.pipeline import (
    ClassifyStage,
    FetchStage,
    ParseStage,
    QualityStage,
    StorageStage,
)


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200, headers: dict | None = None):
        self.text = text
        self.status_code = status_code
        self.headers = headers or {"content-type": "text/html"}


@pytest.mark.asyncio
class TestLinkExtractor:
    async def test_extract_links_filters_and_deduplicates(self):
        html = """
        <a href="#a">Anchor</a>
        <a href="javascript:void(0)">JS</a>
        <a href="/article/1">A1</a>
        <a href="/article/1">A1-dup</a>
        <a href="https://foo.bar/path">Abs</a>
        """
        links = extract_links(html, "https://example.com/base")
        assert links == ["https://example.com/article/1", "https://foo.bar/path"]


@pytest.mark.asyncio
class TestParseStage:
    async def test_parse_stage_extracts_title_content_links(
        self, crawler_item_factory, crawler_sample_html
    ):
        stage = ParseStage()
        item = crawler_item_factory(raw_html=crawler_sample_html)

        result = await stage.process(item)
        assert result is item
        assert item.title == "Test Article"
        assert "crawler sample content" in item.content
        assert "https://example.com/next" in item.links

    async def test_parse_stage_sets_error_when_html_missing(self, crawler_item_factory):
        stage = ParseStage()
        item = crawler_item_factory(raw_html="")

        result = await stage.process(item)
        assert result is item
        assert item.error == "No HTML to parse"

    async def test_parse_stage_skips_when_item_already_failed(self, crawler_item_factory):
        stage = ParseStage()
        item = crawler_item_factory(error="Fetch failed")
        old_title = item.title

        result = await stage.process(item)
        assert result is item
        assert item.title == old_title


@pytest.mark.asyncio
class TestClassifyStage:
    async def test_classify_by_title_pattern(self, crawler_item_factory):
        stage = ClassifyStage()
        item = crawler_item_factory(title="Sign In", url="https://example.com/random")
        result = await stage.process(item)
        assert result.content_type == "functional"

    async def test_classify_by_path_pattern(self, crawler_item_factory):
        stage = ClassifyStage()
        item = crawler_item_factory(title="Any", url="https://example.com/blog/post-1")
        result = await stage.process(item)
        assert result.content_type == "article"

    async def test_classify_default_other(self, crawler_item_factory):
        stage = ClassifyStage()
        item = crawler_item_factory(title="Hello", url="https://example.com/unknown/path")
        result = await stage.process(item)
        assert result.content_type == "other"


@pytest.mark.asyncio
class TestQualityStage:
    async def test_reject_http_error(self, crawler_item_factory):
        stage = QualityStage()
        item = crawler_item_factory(status_code=404, content="a" * 200)
        result = await stage.process(item)
        assert result is None
        assert item.error == "HTTP 404"
        assert item.quality_passed is False

    async def test_reject_functional_path(self, crawler_item_factory):
        stage = QualityStage()
        item = crawler_item_factory(url="https://example.com/login", content="a" * 200)
        result = await stage.process(item)
        assert result is None
        assert item.error == "functional_page"

    async def test_reject_functional_title(self, crawler_item_factory):
        stage = QualityStage()
        item = crawler_item_factory(title="Access Denied", content="a" * 200)
        result = await stage.process(item)
        assert result is None
        assert item.error == "functional_title"

    async def test_reject_too_short_content(self, crawler_item_factory):
        stage = QualityStage()
        item = crawler_item_factory(content="short")
        result = await stage.process(item)
        assert result is None
        assert item.error == "too_short"

    async def test_pass_valid_content(self, crawler_item_factory):
        stage = QualityStage()
        item = crawler_item_factory(content="x" * 100, title="A Story")
        result = await stage.process(item)
        assert result is item
        assert item.quality_passed is True
        assert item.error == ""


@pytest.mark.asyncio
class TestFetchStage:
    async def test_fetch_stage_extracts_html_fields(
        self, monkeypatch, crawler_item_factory, crawler_sample_html
    ):
        stage = FetchStage()
        fake_client = AsyncMock()
        fake_client.get = AsyncMock(return_value=_FakeResponse(crawler_sample_html, 200))
        monkeypatch.setattr(stage, "_get_client", AsyncMock(return_value=fake_client))

        item = crawler_item_factory(url="https://example.com/article/1")
        result = await stage.process(item)
        assert result is item
        assert item.title == "Test Article"
        assert "crawler sample content" in item.content
        assert item.status_code == 200
        assert "https://example.com/next" in item.links

    async def test_fetch_stage_marks_error_on_exception(
        self, monkeypatch, crawler_item_factory
    ):
        stage = FetchStage()
        fake_client = AsyncMock()
        fake_client.get = AsyncMock(side_effect=RuntimeError("boom"))
        monkeypatch.setattr(stage, "_get_client", AsyncMock(return_value=fake_client))

        item = crawler_item_factory()
        result = await stage.process(item)
        assert result is item
        assert item.error.startswith("Fetch failed:")


@pytest.mark.asyncio
class TestStorageStage:
    async def test_storage_stage_fallback_local_write(
        self, monkeypatch, tmp_path, crawler_item_factory
    ):
        monkeypatch.chdir(tmp_path)
        stage = StorageStage(container=None)
        item = crawler_item_factory(
            url="https://example.com/article/1",
            title="A",
            content="x" * 200,
            content_type="article",
        )
        result = await stage.process(item)
        assert result is item
        assert item.oss_path.endswith(".json")
        assert item.file_size > 0
        file_path = tmp_path / "data" / "crawler" / item.oss_path
        saved = json.loads(file_path.read_text(encoding="utf-8"))
        assert saved["url"] == item.url

    async def test_storage_stage_gzip_for_large_payload(
        self, monkeypatch, tmp_path, crawler_item_factory
    ):
        monkeypatch.chdir(tmp_path)
        stage = StorageStage(container=None)
        item = crawler_item_factory(
            url="https://example.com/article/large",
            title="Large",
            content="z" * 60000,
            content_type="article",
        )
        result = await stage.process(item)
        assert result is item
        assert item.oss_path.endswith(".json.gz")
        file_path = tmp_path / "data" / "crawler" / item.oss_path
        raw = gzip.decompress(file_path.read_bytes()).decode("utf-8")
        payload = json.loads(raw)
        assert payload["title"] == "Large"

    async def test_storage_stage_uses_storage_service(self, crawler_item_factory):
        storage = AsyncMock()
        storage.ingest_bytes = AsyncMock(
            return_value={"path": "crawler/x.json", "size": 123}
        )
        container = MagicMock()
        container.is_available.return_value = True
        container.get.return_value = storage
        stage = StorageStage(container=container)

        item = crawler_item_factory(content="x" * 100)
        result = await stage.process(item)
        assert result is item
        assert item.oss_path == "crawler/x.json"
        assert item.file_size == 123
        storage.ingest_bytes.assert_awaited_once()
