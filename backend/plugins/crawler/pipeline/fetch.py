"""Crawler plugin — 抓取车间：纯 HTTP 请求，带上正常浏览器请求头。"""

from __future__ import annotations

import httpx

from backend.plugins.crawler.pipeline.base import BaseStage, CrawlItem


# 正常浏览器请求头
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


class FetchStage(BaseStage):
    """抓取车间：httpx 请求，拿多少是多少，不渲染 JS。"""

    name = "fetch"

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers=_HEADERS,
            )
        return self._client

    async def process(self, item: CrawlItem) -> CrawlItem | None:
        try:
            client = await self._get_client()
            response = await client.get(item.url)
            html = response.text

            import re

            # 提取 title
            title_m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
            title = title_m.group(1).strip() if title_m else ""

            # 提取链接
            links = []
            seen_links: set[str] = set()
            for m in re.finditer(
                r'<a[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE
            ):
                href = m.group(1).strip()
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue
                from urllib.parse import urljoin

                abs_url = urljoin(item.url, href)
                if (
                    abs_url.startswith(("http://", "https://"))
                    and abs_url not in seen_links
                ):
                    seen_links.add(abs_url)
                    links.append(abs_url)

            # 简易文本提取
            text = re.sub(
                r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE
            )
            text = re.sub(
                r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE
            )
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

            item.raw_html = html
            item.html = html
            item.title = title
            item.content = text[:10000]
            item.links = links
            item.status_code = response.status_code
            item.headers = dict(response.headers)
            return item
        except Exception as e:
            item.error = f"Fetch failed: {e}"
            return item

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
