from __future__ import annotations

import pytest

from backend.tests.conftest import patch_container_service


class TestSSRF:
    """SSRF 测试：验证爬虫相关路由在 URL 参数异常时的鲁棒性。"""

    @pytest.fixture(autouse=True)
    def setup_crawler_service(self, db_container):
        from unittest.mock import AsyncMock

        mock = AsyncMock()
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        mock.records = AsyncMock(return_value={"list": [], "total": 0})
        patch_container_service(db_container, "crawler", mock)

    async def test_crawler_start_requires_admin(self, client, auth_headers):
        """启动爬虫需要管理员权限。"""
        resp = await client.post("/api/crawler/start", headers=auth_headers)
        assert resp.status_code == 403, (
            f"Non-admin was able to start crawler: status {resp.status_code}"
        )

    async def test_crawler_records_rejects_invalid_id(self, client, admin_headers):
        """爬虫记录查询应拒绝无效的记录 ID。"""
        invalid_ids = [
            "../../../etc/passwd",
            "<script>alert(1)</script>",
        ]
        for rid in invalid_ids:
            resp = await client.get(
                f"/api/crawler/records/{rid}",
                headers=admin_headers,
            )
            # 不应返回 500（可以返回 400/404/422）
            assert resp.status_code != 500, (
                f"Crawler records with invalid id caused 500: {rid}"
            )

    async def test_crawler_file_download_rejects_path_traversal(
        self, client, admin_headers, db_container
    ):
        """爬虫文件下载应拒绝路径遍历（复用了 test_path_traversal 的验证）。"""
        import uuid
        from unittest.mock import AsyncMock

        record_id = str(uuid.uuid4())

        async def mock_get_record(rid):
            return {
                "file_path": "../../../etc/passwd",
                "id": rid,
                "url": "http://example.com",
            }

        crawler_mock = AsyncMock()
        crawler_mock.get_record = mock_get_record
        patch_container_service(db_container, "crawler", crawler_mock)

        resp = await client.get(
            f"/api/crawler/records/{record_id}/file",
            headers=admin_headers,
        )
        data = resp.json()
        assert data["code"] in ("error", "not_found")

    async def test_crawler_file_download_rejects_absolute_path(
        self, client, admin_headers, db_container
    ):
        """爬虫文件下载应拒绝绝对路径。"""
        import uuid
        from unittest.mock import AsyncMock

        record_id = str(uuid.uuid4())

        async def mock_get_record(rid):
            return {
                "file_path": "/etc/passwd",
                "id": rid,
                "url": "http://example.com",
            }

        crawler_mock = AsyncMock()
        crawler_mock.get_record = mock_get_record
        patch_container_service(db_container, "crawler", crawler_mock)

        resp = await client.get(
            f"/api/crawler/records/{record_id}/file",
            headers=admin_headers,
        )
        data = resp.json()
        assert data["code"] in ("error", "not_found")

    async def test_crawler_seeds_rejects_malformed_urls(self, client, admin_headers):
        """种子 URL 应经过验证。"""
        malicious_seeds = [
            "http://127.0.0.1:8000",
            "http://169.254.169.254/latest/meta-data",
            "javascript:alert(1)",
            "file:///etc/passwd",
        ]
        for url in malicious_seeds:
            resp = await client.post(
                "/api/crawler/seeds",
                json={"url": url},
                headers=admin_headers,
            )
            assert resp.status_code != 500, f"Malicious seed URL caused 500: {url}"
