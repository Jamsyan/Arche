"""Crawler plugin — URL deduplication with normalization."""

from __future__ import annotations

from urllib.parse import parse_qs, urlencode, urlparse


class URLDedup:
    """URL 去重器：规范化 URL 后判断是否已访问。"""

    def __init__(self):
        self._seen: set[str] = set()

    @staticmethod
    def normalize(url: str) -> str:
        """规范化 URL：小写 host、去掉 fragment、排序 query params、去掉默认端口。"""
        parsed = urlparse(url)
        host = parsed.hostname.lower() if parsed.hostname else ""

        # 去掉默认端口
        if (parsed.scheme == "http" and parsed.port == 80) or \
           (parsed.scheme == "https" and parsed.port == 443):
            netloc = host
        else:
            netloc = parsed.netloc.lower()

        # 规范化路径：去掉尾部斜杠（根路径除外）
        path = parsed.path.rstrip("/") if parsed.path != "/" else parsed.path

        # 排序 query params
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=True)
            sorted_query = urlencode(sorted(params.items()), doseq=True)
        else:
            sorted_query = ""

        return f"{parsed.scheme}://{netloc}{path}?{sorted_query}" if sorted_query else f"{parsed.scheme}://{netloc}{path}"

    def is_new(self, url: str) -> bool:
        """判断 URL 是否未访问过。"""
        normalized = self.normalize(url)
        return normalized not in self._seen

    def mark_seen(self, url: str) -> None:
        """标记 URL 为已访问。"""
        self._seen.add(self.normalize(url))

    def clear(self) -> None:
        """清空所有记录。"""
        self._seen.clear()
