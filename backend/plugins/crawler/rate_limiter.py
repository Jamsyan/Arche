"""Crawler plugin — Per-domain rate limiter."""

from __future__ import annotations

import asyncio
import time
from urllib.parse import urlparse


class RateLimiter:
    """Per-domain 速率限制器：确保同一域名的请求间隔 >= min_interval。"""

    def __init__(self, min_interval: float = 1.0):
        self._min_interval = min_interval
        self._last_request: dict[str, float] = {}
        self._lock = asyncio.Lock()

    def _get_domain(self, url: str) -> str:
        return urlparse(url).hostname.lower() or ""

    async def wait(self, url: str) -> None:
        """等待到可以发起请求的时间。"""
        domain = self._get_domain(url)
        if not domain:
            return

        async with self._lock:
            now = time.monotonic()
            last = self._last_request.get(domain, 0)
            elapsed = now - last

            if elapsed < self._min_interval:
                sleep_time = self._min_interval - elapsed
                self._last_request[domain] = time.monotonic() + sleep_time
            else:
                self._last_request[domain] = now

        if elapsed < self._min_interval:
            await asyncio.sleep(sleep_time)

    def update_interval(self, seconds: float) -> None:
        """更新最小请求间隔。"""
        self._min_interval = seconds
