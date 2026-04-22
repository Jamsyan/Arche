"""Crawler plugin — 分类车间：页面类型分类打标。"""

from __future__ import annotations

from urllib.parse import urlparse

from backend.plugins.crawler.pipeline.base import BaseStage, CrawlItem

# URL 路径模式 → 内容类型
_PATH_PATTERNS = {
    "article": ["/article", "/blog", "/post", "/news", "/story", "/p/", "/detail"],
    "post": ["/question", "/answer", "/thread", "/topic", "/t/", "/q/"],
    "product": ["/product", "/item", "/goods", "/shop", "/store"],
    "nav": ["/category", "/tag", "/label", "/index", "/sitemap", "/map"],
}

# title 特征
_TITLE_PATTERNS = {
    "article": ["article", "blog", "news", "story"],
    "post": ["question", "answer", "thread", "discussion"],
    "ad": ["广告", "promotion", "sponsor"],
    "functional": ["login", "register", "sign in", "sign up", "captcha"],
}


class ClassifyStage(BaseStage):
    """分类车间：基于 URL 路径、title、HTML 结构特征判断页面类型。"""

    name = "classify"

    async def process(self, item: CrawlItem) -> CrawlItem | None:
        if item.error:
            return item

        content_type = self._classify(item)
        item.content_type = content_type
        return item

    def _classify(self, item: CrawlItem) -> str:
        path = urlparse(item.url).path.lower()
        title = item.title.lower() if item.title else ""

        # 先检查 title 特征
        for ctype, patterns in _TITLE_PATTERNS.items():
            if any(p in title for p in patterns):
                return ctype

        # 再检查 URL 路径
        for ctype, patterns in _PATH_PATTERNS.items():
            if any(p in path for p in patterns):
                return ctype

        # 默认
        return "other"
