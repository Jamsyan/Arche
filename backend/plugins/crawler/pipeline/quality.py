"""爬虫插件 —— 质检车间：排除功能性页面。"""

from __future__ import annotations

from urllib.parse import urlparse

from backend.plugins.crawler.pipeline.base import BaseStage, CrawlItem

# 功能性页面 URL 路径关键词
_FUNCTIONAL_PATHS = [
    "/login",
    "/signin",
    "/signup",
    "/register",
    "/auth",
    "/logout",
    "/forgot-password",
    "/reset-password",
    "/verify",
    "/captcha",
    "/challenge",
    "/consent",
    "/cookie",
    "/settings",
    "/profile",
    "/account",
    "/preferences",
]

# 功能性页面 title 关键词
_FUNCTIONAL_TITLES = [
    "login",
    "sign in",
    "register",
    "sign up",
    "captcha",
    "verify",
    "access denied",
]


class QualityStage(BaseStage):
    """质检车间：排除登录/注册/404/纯广告/纯导航等无意义页面。"""

    name = "quality"

    async def process(self, item: CrawlItem) -> CrawlItem | None:
        # HTTP 错误
        if item.status_code and item.status_code >= 400:
            item.quality_passed = False
            item.error = f"HTTP {item.status_code}"
            return None

        # 功能性页面检查
        path = urlparse(item.url).path.lower()
        if any(p in path for p in _FUNCTIONAL_PATHS):
            item.quality_passed = False
            item.error = "functional_page"
            return None

        # title 功能性特征
        title = item.title.lower() if item.title else ""
        if any(p in title for p in _FUNCTIONAL_TITLES):
            item.quality_passed = False
            item.error = "functional_title"
            return None

        # 内容太短（少于 30 字符）
        if len(item.content.strip()) < 30:
            item.quality_passed = False
            item.error = "too_short"
            return None

        return item
