"""Crawler plugin — Playwright browser manager for headless page rendering."""

from __future__ import annotations

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserManager:
    """管理 Playwright 浏览器实例的生命周期。"""

    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def startup(self) -> None:
        """启动浏览器实例。"""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        self._context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Veil-Crawler/0.1.0",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )

    async def shutdown(self) -> None:
        """关闭浏览器实例。"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def fetch_page(self, url: str, timeout: int = 30000) -> dict:
        """抓取单个页面，返回 HTML 和元数据。

        Args:
            url: 目标 URL
            timeout: 超时时间（毫秒）

        Returns:
            {html, title, text, final_url, status_code, headers, links}
        """
        if not self._context:
            raise RuntimeError("浏览器未启动，请先调用 startup()")

        page: Page = await self._context.new_page()
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            if not response:
                return {
                    "html": "",
                    "title": None,
                    "text": "",
                    "final_url": url,
                    "status_code": 0,
                    "headers": {},
                    "links": [],
                }

            html = await page.content()
            title = await page.title()
            text = await page.inner_text("body") if await page.query_selector("body") else ""
            final_url = page.url

            # 提取页面内所有链接
            links = []
            elements = await page.query_selector_all("a[href]")
            for el in elements:
                href = await el.get_attribute("href")
                if href:
                    links.append(href)

            return {
                "html": html,
                "title": title,
                "text": text[:10000],  # 限制文本长度
                "final_url": final_url,
                "status_code": response.status,
                "headers": dict(response.headers),
                "links": links,
            }
        finally:
            await page.close()
