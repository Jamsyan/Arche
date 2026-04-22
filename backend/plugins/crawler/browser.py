"""Crawler plugin — BrowserManager：Playwright 浏览器池，单实例多 tab 复用。"""

from __future__ import annotations

from playwright.async_api import async_playwright


class BrowserManager:
    """Playwright 浏览器管理器：启动 headless Chromium，复用 BrowserContext。"""

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None

    async def startup(self) -> None:
        """启动浏览器实例。"""
        self._playwright = await async_playwright.start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        self._context = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )

    async def shutdown(self) -> None:
        """关闭浏览器。"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def new_page(self):
        """创建一个新 Page 实例（新 tab）。"""
        if not self._context:
            raise RuntimeError("Browser not started")
        return await self._context.new_page()

    async def fetch_page(self, url: str, timeout: int = 30000) -> dict:
        """用新 tab 抓取页面，返回渲染后的内容。"""
        page = await self.new_page()
        try:
            response = await page.goto(
                url, wait_until="domcontentloaded", timeout=timeout
            )
            status_code = response.status if response else 0
            headers = response.headers if response else {}
            html = await page.content()
            title = await page.title()
            text = (await page.inner_text("body"))[:10000]
            links = [
                href
                for el in await page.query_selector_all("a[href]")
                if (href := el.get_attribute("href"))
            ]
            return {
                "html": html,
                "title": title,
                "text": text,
                "final_url": page.url,
                "status_code": status_code,
                "headers": headers,
                "links": links,
            }
        finally:
            await page.close()
