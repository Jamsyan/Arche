"""Crawler plugin — Link extraction from HTML content."""

from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


class _LinkExtractor(HTMLParser):
    """HTML 解析器，提取 <a href> 链接。"""

    def __init__(self):
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)


def extract_links(html: str, base_url: str) -> list[str]:
    """从 HTML 中提取并规范化链接。

    过滤规则：
    - 非 http/https 协议（去掉 javascript:, mailto:, # 等）
    - 规范化为绝对 URL
    """
    parser = _LinkExtractor()
    try:
        parser.feed(html)
    except Exception:
        return []

    base = urlparse(base_url)
    result = []
    seen = set()

    for href in parser.links:
        # 跳过锚点和特殊协议
        href = href.strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        # 转为绝对 URL
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)

        # 只保留 http/https
        if parsed.scheme not in ("http", "https"):
            continue

        # 规范化：去掉 fragment，统一小写 host
        normalized = f"{parsed.scheme}://{parsed.hostname.lower()}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"

        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result
