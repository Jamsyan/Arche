"""Sensitive word filter — loads words from config and checks text content."""

from __future__ import annotations


class SensitiveWordFilter:
    """Simple string-matching sensitive word filter."""

    def __init__(self, words: list[str] | None = None):
        self._words: list[str] = words or []

    def check(self, text: str) -> tuple[bool, list[str]]:
        """检查文本是否包含敏感词。

        Returns:
            (通过, 匹配到的敏感词列表)
        """
        if not self._words or not text:
            return True, []

        text_lower = text.lower()
        matched = [w for w in self._words if w.lower() in text_lower]
        return len(matched) == 0, matched


# Module-level singleton，延迟初始化
_filter: SensitiveWordFilter | None = None


def init_filter(words: list[str] | None = None) -> SensitiveWordFilter:
    """初始化全局敏感词过滤器。"""
    global _filter
    _filter = SensitiveWordFilter(words)
    return _filter


def get_filter() -> SensitiveWordFilter:
    """获取全局过滤器实例。"""
    global _filter
    if _filter is None:
        _filter = SensitiveWordFilter()
    return _filter
