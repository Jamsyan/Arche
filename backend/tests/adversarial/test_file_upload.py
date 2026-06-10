from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from backend.tests.conftest import patch_container_service
from backend.plugins.oss.services import ALLOWED_MIME_TYPES


def _validate_mime(content_type):
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        from backend.core.middleware import AppError

        raise AppError(
            f"不支持的文件类型: {content_type}",
            code="file_type_not_allowed",
            status_code=415,
        )


def _validate_filename(filename):
    if ".." in filename or "/" in filename or "\\" in filename:
        from backend.core.middleware import AppError

        raise AppError("文件名包含非法字符", code="invalid_filename", status_code=400)


def _make_mock_storage():
    mock = AsyncMock()

    async def upload_file(file, owner_id, user_level=5, is_private=False):
        _validate_mime(file.content_type)
        filename = file.filename or "unnamed"
        _validate_filename(filename)
        content = await file.read()
        return {
            "id": "mock-id",
            "owner_id": str(owner_id),
            "path": f"users/{owner_id}/{filename}",
            "size": len(content),
            "mime_type": file.content_type,
            "storage_type": "local",
            "is_private": is_private,
        }

    mock.upload_file = upload_file
    return mock


class TestFileUploadSecurity:
    @pytest.fixture(autouse=True)
    def setup_storage_service(self, db_container):
        mock = _make_mock_storage()
        patch_container_service(db_container, "storage", mock)

    async def test_mismatched_mime_type(self, client, auth_headers):
        shell_script = b"#!/bin/bash\necho pwned"
        resp = await client.post(
            "/api/oss/upload",
            files={"file": ("exploit.sh", shell_script, "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code != 500, "MIME mismatch caused 500"
        data = resp.json()
        if resp.status_code == 200:
            assert data["code"] == "ok"
        else:
            assert "code" in data

    async def test_special_chars_in_filename(self, client, auth_headers):
        resp = await client.post(
            "/api/oss/upload",
            files={"file": ("foo<>bar.txt", b"test content", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code != 500, "Special chars filename caused 500"
        data = resp.json()
        if resp.status_code == 200:
            assert data["code"] == "ok"
        else:
            assert "code" in data

    async def test_zero_byte_file(self, client, auth_headers):
        resp = await client.post(
            "/api/oss/upload",
            files={"file": ("empty.png", b"", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code != 500, "Zero-byte file caused 500"
        data = resp.json()
        if resp.status_code == 200:
            assert data["code"] == "ok"
        else:
            assert "code" in data

    async def test_double_extension(self, client, auth_headers):
        resp = await client.post(
            "/api/oss/upload",
            files={
                "file": (
                    "shell.php.jpg",
                    b"<?php system($_GET['cmd']); ?>",
                    "image/jpeg",
                )
            },
            headers=auth_headers,
        )
        assert resp.status_code != 500, "Double extension file caused 500"
        data = resp.json()
        if resp.status_code == 200:
            assert data["code"] == "ok"
        else:
            assert "code" in data
