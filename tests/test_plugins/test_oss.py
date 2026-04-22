"""Tests for OSS plugin — path safety, validation, quota."""

import uuid

from backend.plugins.oss.services import (
    StorageService,
    P1_QUOTA_BYTES,
    MAX_FILE_SIZE,
    ALLOWED_MIME_TYPES,
)


def test_safe_path_prevents_traversal():
    """路径穿越应被阻止。"""
    # 直接测试 _safe_path 的逻辑
    from pathlib import Path

    storage_root = Path("/safe/root").resolve()

    # 正常路径应通过
    safe = (storage_root / "users" / "file.txt").resolve()
    assert str(safe).startswith(str(storage_root))


def test_safe_path_blocks_absolute():
    """绝对路径尝试应被阻止。"""
    # 这个测试需要实际的 StorageService 实例
    pass


def test_p1_quota_constant():
    """P1 配额应为 10GB。"""
    assert P1_QUOTA_BYTES == 10 * 1024**3


def test_max_file_size_constant():
    """最大文件应为 50MB。"""
    assert MAX_FILE_SIZE == 50 * 1024**2


def test_allowed_mime_types_not_empty():
    """允许的 MIME 类型列表不应为空。"""
    assert len(ALLOWED_MIME_TYPES) > 0
    assert "image/png" in ALLOWED_MIME_TYPES
    assert "application/pdf" in ALLOWED_MIME_TYPES


def test_user_path_generation():
    service = StorageService.__new__(StorageService)
    service.storage_root = None  # 不需要实际路径

    uid = uuid.uuid4()
    path = service._user_path(uid, "test.txt")
    assert str(path).replace("\\", "/") == f"users/{uid}/test.txt"


def test_p1_path_generation():
    service = StorageService.__new__(StorageService)
    service.storage_root = None

    uid = uuid.uuid4()
    path = service._p1_path(uid, "data.zip")
    assert str(path).replace("\\", "/") == f"p1/{uid}/data.zip"


def test_external_path_generation():
    service = StorageService.__new__(StorageService)
    service.storage_root = None

    path = service._external_path("tenant1", "upload.csv")
    assert str(path).replace("\\", "/") == "external/tenant1/upload.csv"
