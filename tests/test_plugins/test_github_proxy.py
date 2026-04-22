"""Tests for GitHub Proxy plugin — rate limiting and cache."""

import pytest
import time

from backend.core.middleware import AppError
from backend.plugins.github_proxy.services import (
    GitHubProxyService,
    CacheEntry,
    RATE_LIMIT_MAX_REQUESTS,
)


class MockConfig:
    def get(self, key, default=None):
        vals = {
            "GITHUB_API_BASE": "https://api.github.com",
            "GITHUB_RAW_BASE": "https://raw.githubusercontent.com",
            "GITHUB_CACHE_TTL": 300,
            "GITHUB_TIMEOUT": 30,
        }
        return vals.get(key, default)

    def get_required(self, key):
        if key == "GITHUB_TOKEN":
            return "test-token"
        raise RuntimeError(f"Required config '{key}' is not set")


class MockContainer:
    def get(self, name):
        if name == "config":
            return MockConfig()
        raise KeyError(name)


def make_service():
    return GitHubProxyService(MockContainer())


def test_rate_limit_allows_normal_traffic():
    service = make_service()
    user_id = "test-user"
    # 发送 MAX_REQUESTS 个请求应全部通过
    for i in range(RATE_LIMIT_MAX_REQUESTS):
        service._check_rate_limit(user_id)


def test_rate_limit_blocks_excess_traffic():
    service = make_service()
    user_id = "test-user"

    for i in range(RATE_LIMIT_MAX_REQUESTS):
        service._check_rate_limit(user_id)

    with pytest.raises(AppError, match="请求过于频繁"):
        service._check_rate_limit(user_id)


def test_rate_limit_per_user_isolation():
    service = make_service()

    for i in range(RATE_LIMIT_MAX_REQUESTS):
        service._check_rate_limit("user-a")

    # 用户 B 应不受影响
    service._check_rate_limit("user-b")


def test_cache_entry_expiration():
    # ttl=-1 确保 expires_at 是过去时间
    entry = CacheEntry(data={"test": True}, status_code=200, headers={}, ttl=-1)
    time.sleep(0.01)
    assert entry.is_expired is True


def test_cache_entry_not_expired():
    entry = CacheEntry(data={"test": True}, status_code=200, headers={}, ttl=600)
    assert entry.is_expired is False


def test_cache_hit_and_miss():
    service = make_service()

    key = "test-cache-key"
    service._set_cache(key, {"data": "test"}, 200, {})

    result = service._get_cached(key)
    assert result is not None
    assert result.data == {"data": "test"}

    # 不存在的 key
    assert service._get_cached("nonexistent") is None


def test_cache_clear():
    service = make_service()
    service._set_cache("key1", "a", 200, {})
    service._set_cache("key2", "b", 200, {})

    count = service.clear_cache()
    assert count == 2
    assert len(service._cache) == 0
