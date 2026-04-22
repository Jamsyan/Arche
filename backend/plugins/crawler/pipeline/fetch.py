"""Crawler plugin — 抓取车间：Playwright 正式抓取。"""

from __future__ import annotations

from backend.plugins.crawler.pipeline.base import BaseStage, CrawlItem


class FetchStage(BaseStage):
    """抓取车间：复用 BrowserManager，用新 tab 打开页面获取完整渲染内容。"""

    name = "fetch"

    def __init__(self, browser_manager=None):
        self._browser = browser_manager

    def set_browser(self, browser_manager):
        self._browser = browser_manager

    async def process(self, item: CrawlItem) -> CrawlItem | None:
        if not self._browser:
            item.error = "BrowserManager not available"
            return item

        try:
            data = await self._browser.fetch_page(item.url)
            item.html = data.get("html", "")
            item.title = data.get("title", "")
            item.content = data.get("text", "")
            item.raw_html = data.get("html", "")
            item.links = data.get("links", [])
            item.status_code = data.get("status_code", 0)
            item.headers = data.get("headers", {})
            return item
        except Exception as e:
            item.error = f"Fetch failed: {e}"
            return item
