"""Crawler plugin — robots.txt compliance checker."""

from __future__ import annotations

import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx


class RobotsChecker:
    """按域名缓存 robots.txt 解析结果，自动遵守 robots 协议。"""

    def __init__(self, user_agent: str = "Veil Crawler", cache_ttl: int = 3600):
        self._user_agent = user_agent
        self._cache_ttl = cache_ttl
        self._parsers: dict[str, tuple[RobotFileParser, float]] = {}

    def _get_domain(self, url: str) -> str:
        return urlparse(url).hostname.lower() or ""

    async def _fetch_robots(self, domain: str) -> RobotFileParser:
        """获取并解析指定域名的 robots.txt。"""
        rp = RobotFileParser()
        url = f"https://{domain}/robots.txt"

        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    # 无 robots.txt 或无法访问，默认允许所有
                    rp.parse(["User-agent: *", "Allow: /"])
        except Exception:
            rp.parse(["User-agent: *", "Allow: /"])

        return rp

    async def is_allowed(self, url: str) -> bool:
        """检查是否允许爬取指定 URL。"""
        domain = self._get_domain(url)
        if not domain:
            return True

        now = time.time()

        # 检查缓存
        if domain in self._parsers:
            parser, cached_at = self._parsers[domain]
            if now - cached_at < self._cache_ttl:
                return parser.can_fetch(self._user_agent, url)

        # 获取新的 robots.txt
        parser = await self._fetch_robots(domain)
        self._parsers[domain] = (parser, now)
        return parser.can_fetch(self._user_agent, url)
