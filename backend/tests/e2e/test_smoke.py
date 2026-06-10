"""E2E 冒烟测试：验证前后端能正常响应。"""

import pytest


@pytest.mark.e2e
class TestSmoke:
    """基础冒烟测试。"""

    async def test_frontend_responds(self, page, frontend_url):
        """前端页面能正常加载。"""
        await page.goto(frontend_url, wait_until="networkidle")
        title = await page.title()
        assert title is not None

    async def test_frontend_has_content(self, page, frontend_url):
        """页面有可见内容（非白屏）。"""
        await page.goto(frontend_url, wait_until="networkidle")
        body_text = await page.inner_text("body")
        assert len(body_text.strip()) > 0

    async def test_backend_health(self, page):
        """后端 API 健康检查。"""
        response = await page.request.get("http://localhost:8000/api/ping")
        assert response.ok

    async def test_page_not_crash(self, page, frontend_url):
        """页面无 JS 崩溃。"""
        errors = []

        def on_error(msg):
            errors.append(msg)

        page.on("pageerror", on_error)
        await page.goto(frontend_url, wait_until="networkidle")
        await page.wait_for_timeout(2000)
        assert len(errors) == 0, f"页面 JS 错误: {errors}"
