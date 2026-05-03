"""SeedManager 单元测试。"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from backend.plugins.crawler.seed_manager import SeedManager


def _make_container(seeds: str = ""):
    container = MagicMock()
    config = MagicMock()
    config.get.return_value = seeds
    container.get.return_value = config
    return container


class TestSeedManager:
    @pytest.mark.asyncio
    async def test_initialize_loads_env_seeds(self):
        container = _make_container("https://a.com,https://b.com/path")
        manager = SeedManager(container)
        await manager.initialize()
        assert manager.queue_size == 2
        assert manager.total_seen == 2

    def test_add_seed_normalize_and_dedupe(self):
        manager = SeedManager(_make_container())
        assert manager.add_seed("https://Example.com/path/") is True
        assert manager.add_seed("https://example.com/path") is False
        assert manager.queue_size == 1

    def test_add_seed_reject_invalid_or_blacklisted(self):
        manager = SeedManager(_make_container())
        manager.add_to_blacklist("evil.com")
        assert manager.add_seed("not-a-url") is False
        assert manager.add_seed("https://evil.com/post") is False

    def test_pop_seed_fifo(self):
        manager = SeedManager(_make_container())
        manager.add_seed("https://a.com/1")
        manager.add_seed("https://a.com/2")
        assert manager.pop_seed() == "https://a.com/1"
        assert manager.pop_seed() == "https://a.com/2"
        assert manager.pop_seed() is None

    def test_blacklist_whitelist_match(self):
        manager = SeedManager(_make_container())
        manager.add_to_blacklist("foo.com")
        manager.add_to_whitelist("bar.com")
        assert manager.is_blacklisted("https://foo.com/x")
        assert manager.is_whitelisted("https://bar.com/x")

    def test_process_sniff_result_functional_adds_blacklist(self):
        manager = SeedManager(_make_container())
        result = manager.process_sniff_result(
            "https://foo.com/login", {"is_functional": True, "has_content": True}
        )
        assert result is False
        assert manager.get_blacklist() == ["foo.com"]

    def test_process_sniff_result_content_adds_seed(self):
        manager = SeedManager(_make_container())
        result = manager.process_sniff_result(
            "https://foo.com/post", {"is_functional": False, "has_content": True}
        )
        assert result is True
        assert manager.queue_size == 1

    def test_discover_seeds_filters_invalid_duplicate_blacklist(self):
        manager = SeedManager(_make_container())
        manager.add_seed("https://foo.com/old")
        manager.add_to_blacklist("evil.com")
        discovered = manager.discover_seeds_from_links(
            [
                "https://foo.com/old",
                "https://foo.com/new",
                "https://evil.com/bad",
                "not-url",
            ],
            "https://foo.com/src",
        )
        assert discovered == ["https://foo.com/new"]
