"""GitHub Proxy Service — 反向代理 GitHub API，支持缓存、Token 注入和限流。"""

from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Any

import httpx

from backend.core.middleware import AppError

if TYPE_CHECKING:
    from backend.core.container import ServiceContainer


class GitHubProxyError(AppError):
    def __init__(
        self,
        message: str = "GitHub 代理请求失败",
        code: str = "github_proxy_error",
        status_code: int = 502,
    ):
        super().__init__(message, code, status_code)


# === 限流常量 ===
RATE_LIMIT_WINDOW = 60  # 秒
RATE_LIMIT_MAX_REQUESTS = 60  # 每分钟最大请求数


class CacheEntry:
    """简单的内存缓存条目。"""

    def __init__(
        self, data: Any, status_code: int, headers: dict[str, str], ttl: int = 300
    ):
        self.data = data
        self.status_code = status_code
        self.headers = headers
        self.expires_at = time.monotonic() + ttl

    @property
    def is_expired(self) -> bool:
        return time.monotonic() > self.expires_at


class GitHubProxyService:
    """GitHub API 反向代理服务：转发请求、缓存响应、注入 Token、限流。"""

    def __init__(self, container: "ServiceContainer"):
        self.container = container
        config = container.get("config")
        self.github_token = config.get_required("GITHUB_TOKEN")
        self.base_url = config.get("GITHUB_API_BASE", "https://api.github.com")
        self.raw_base_url = config.get(
            "GITHUB_RAW_BASE", "https://raw.githubusercontent.com"
        )
        self.default_ttl = config.get("GITHUB_CACHE_TTL", 300)
        self.timeout = config.get("GITHUB_TIMEOUT", 30)

        self._cache: dict[str, CacheEntry] = {}
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
        )

        # 限流追踪：{user_id: [timestamp, ...]}
        self._rate_tracker: dict[str, list[float]] = defaultdict(list)

    def _check_rate_limit(self, user_id: str) -> None:
        """检查用户是否在限流窗口内超出请求数。"""
        now = time.monotonic()
        timestamps = self._rate_tracker[user_id]

        # 清理过期时间戳
        cutoff = now - RATE_LIMIT_WINDOW
        self._rate_tracker[user_id] = [t for t in timestamps if t > cutoff]
        timestamps = self._rate_tracker[user_id]

        if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
            raise AppError(
                f"请求过于频繁，请等待 {RATE_LIMIT_WINDOW} 秒后重试",
                code="rate_limit_exceeded",
                status_code=429,
            )

        timestamps.append(now)

    async def close(self) -> None:
        await self._client.aclose()

    def _cache_key(self, method: str, path: str, params: dict) -> str:
        raw = f"{method}:{path}:{sorted(params.items())}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_cached(self, key: str) -> CacheEntry | None:
        entry = self._cache.get(key)
        if entry and not entry.is_expired:
            return entry
        if entry:
            del self._cache[key]
        return None

    def _set_cache(
        self,
        key: str,
        data: Any,
        status_code: int,
        headers: dict[str, str],
        ttl: int | None = None,
    ) -> None:
        if ttl is None:
            ttl = self.default_ttl
        if ttl > 0:
            self._cache[key] = CacheEntry(data, status_code, headers, ttl)

    def _build_headers(
        self, extra_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        """构建转发到 GitHub 的请求头，替换 Authorization 为配置的 Token。"""
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Veil-GitHub-Proxy/0.1.0",
        }
        if extra_headers:
            skip = {"authorization", "host", "connection", "content-length"}
            for k, v in extra_headers.items():
                if k.lower() not in skip:
                    headers[k] = v
        return headers

    async def proxy_request(
        self,
        method: str,
        path: str,
        query_params: dict | None = None,
        headers: dict | None = None,
        body: bytes | None = None,
        user_id: str | None = None,
    ) -> dict:
        """代理转发请求到 GitHub API。"""
        # 限流检查
        if user_id:
            self._check_rate_limit(user_id)

        query_params = query_params or {}
        cache_key = self._cache_key(method, path, query_params)

        if method.upper() == "GET":
            cached = self._get_cached(cache_key)
            if cached:
                return {
                    "data": cached.data,
                    "status_code": cached.status_code,
                    "headers": cached.headers,
                    "cached": True,
                }

        proxied_headers = self._build_headers(headers)

        try:
            response = await self._client.request(
                method=method.upper(),
                url=f"/{path.lstrip('/')}",
                params=query_params,
                headers=proxied_headers,
                content=body,
            )
        except httpx.TimeoutException:
            raise GitHubProxyError(
                "GitHub API 请求超时", code="github_timeout", status_code=504
            )
        except httpx.ConnectError:
            raise GitHubProxyError(
                "无法连接 GitHub", code="github_connect_error", status_code=502
            )

        status_code = response.status_code

        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}

        resp_headers = dict(response.headers)

        if method.upper() == "GET" and 200 <= status_code < 300:
            cache_control = resp_headers.get("Cache-Control", "")
            ttl = self._parse_cache_ttl(cache_control)
            self._set_cache(cache_key, data, status_code, resp_headers, ttl)

        x_cache_status = (
            "HIT"
            if (method.upper() == "GET" and self._get_cached(cache_key))
            else "MISS"
        )

        return {
            "data": data,
            "status_code": status_code,
            "headers": resp_headers,
            "cached": x_cache_status == "HIT",
        }

    async def proxy_raw_content(self, path: str) -> dict:
        """代理 GitHub 静态资源（raw.githubusercontent.com）。"""
        cache_key = self._cache_key("GET", f"raw:{path}", {})
        cached = self._get_cached(cache_key)
        if cached:
            return {
                "data": cached.data,
                "status_code": cached.status_code,
                "headers": cached.headers,
                "cached": True,
            }

        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True
        ) as client:
            try:
                response = await client.get(f"{self.raw_base_url}/{path.lstrip('/')}")
            except httpx.TimeoutException:
                raise GitHubProxyError(
                    "GitHub 静态资源请求超时", code="github_timeout", status_code=504
                )
            except httpx.ConnectError:
                raise GitHubProxyError(
                    "无法连接 GitHub", code="github_connect_error", status_code=502
                )

            status_code = response.status_code
            content = response.content
            resp_headers = dict(response.headers)

            if 200 <= status_code < 300:
                ttl = self._parse_cache_ttl(resp_headers.get("Cache-Control", ""))
                self._set_cache(cache_key, content, status_code, resp_headers, ttl)

            return {
                "data": content,
                "status_code": status_code,
                "headers": resp_headers,
                "cached": False,
            }

    def _parse_cache_ttl(self, cache_control: str) -> int | None:
        """从 Cache-Control 头解析 TTL。"""
        if not cache_control:
            return None
        for part in cache_control.split(","):
            part = part.strip()
            if part.startswith("max-age="):
                try:
                    return int(part.split("=", 1)[1])
                except ValueError:
                    pass
            if part == "no-cache" or part == "no-store":
                return 0
        return None

    def clear_cache(self) -> int:
        """清空所有缓存，返回清空的条目数。"""
        count = len(self._cache)
        self._cache.clear()
        return count
