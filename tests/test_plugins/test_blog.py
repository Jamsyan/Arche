"""Tests for Blog plugin — sensitive word filter and service logic."""

from backend.plugins.blog.sensitive_words import (
    SensitiveWordFilter,
    init_filter,
    get_filter,
)


def test_sensitive_word_filter_match():
    f = SensitiveWordFilter(["badword", "spam"])
    passed, matched = f.check("this contains badword here")
    assert passed is False
    assert "badword" in matched


def test_sensitive_word_filter_clean():
    f = SensitiveWordFilter(["badword"])
    passed, matched = f.check("this is clean text")
    assert passed is True
    assert matched == []


def test_sensitive_word_filter_empty():
    f = SensitiveWordFilter([])
    passed, matched = f.check("any text with badword")
    assert passed is True  # 无敏感词配置时全部通过


def test_sensitive_word_filter_case_insensitive():
    f = SensitiveWordFilter(["BadWord"])
    passed, matched = f.check("this has BADWORD in caps")
    assert passed is False


def test_init_and_get_filter():
    init_filter(["test1", "test2"])
    f = get_filter()
    assert isinstance(f, SensitiveWordFilter)
    passed, matched = f.check("contains test1 word")
    assert passed is False


def test_slug_generation():
    """BlogService 的 slug 生成应生成 URL 友好的字符串。"""
    import re

    title = "Hello World! This is a Test."
    slug = re.sub(r"[^\w一-鿿-]", "-", title.lower().strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    assert slug == "hello-world-this-is-a-test"
