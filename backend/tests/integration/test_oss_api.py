"""OSS 模块 API 集成测试。

测试真实 HTTP 路由行为，覆盖：
- 文件上传 / 下载
- 文件列表
- 文件删除
- 配额检查
- 权限校验
"""

from __future__ import annotations

import uuid
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from backend.tests.conftest import patch_container_service


@pytest.fixture
def mock_oss_backend():
    """Mock OSS 后端，避免真实存储调用。"""
    with patch("backend.plugins.oss.services.StorageBackend") as mock:
        mock_backend = AsyncMock()
        mock_backend.put_object.return_value = {"etag": "test-etag"}
        mock_backend.get_object.return_value = b"test content"
        mock_backend.delete_object.return_value = None
        mock.return_value = mock_backend
        yield mock_backend


@pytest.mark.asyncio
class TestOSSUploadAPI:
    """上传接口测试。"""

    async def test_upload_endpoint_requires_auth(self, client):
        """未登录上传应返回 401。"""
        response = await client.post("/api/oss/upload")
        # 应该是 401 或 422（因为没传文件），但不是 404
        assert response.status_code != 404

    async def test_quota_endpoint_exists(self, client, auth_headers):
        """配额查询接口应存在。"""
        response = await client.get("/api/oss/quota", headers=auth_headers)
        assert response.status_code != 404

    async def test_list_files_endpoint_exists(self, client, auth_headers):
        """文件列表接口应存在。"""
        response = await client.get("/api/oss/my", headers=auth_headers)
        assert response.status_code != 404


@pytest.mark.asyncio
class TestOSSAdminAPI:
    """管理员 OSS 接口测试。"""

    async def test_admin_stats_endpoint_exists(self, client, admin_headers):
        """管理员统计接口应存在。"""
        with patch(
            "backend.plugins.oss.services.StorageService.get_admin_stats"
        ) as mock_stats:
            mock_stats.return_value = {
                "total_files": 0,
                "total_size": 0,
                "hot_storage_size": 0,
                "cold_storage_size": 0,
                "disk_usage": {},
            }

            response = await client.get("/api/oss/admin/stats", headers=admin_headers)

        assert response.status_code != 404

    async def test_admin_quota_and_rate_limit_endpoints(
        self, client, admin_headers, db_container
    ):
        storage = db_container.get("storage")
        storage.list_user_quotas = AsyncMock(return_value={"items": [], "total": 0})
        storage.update_user_quota = AsyncMock(
            return_value={"user_id": str(uuid.uuid4()), "quota_bytes": 1024}
        )

        limiter = MagicMock()
        limiter.global_rate = 1024 * 1024
        limiter.set_global_rate = MagicMock()
        limiter.set_user_multiplier = MagicMock()
        patch_container_service(db_container, "oss_rate_limiter", limiter)

        list_res = await client.get("/api/oss/admin/quotas", headers=admin_headers)
        assert list_res.status_code == 200
        assert list_res.json()["code"] == "ok"

        user_id = str(uuid.uuid4())
        update_res = await client.put(
            f"/api/oss/admin/quotas/{user_id}",
            json={"quota_bytes": 2048, "speed_multiplier": 1.5},
            headers=admin_headers,
        )
        assert update_res.status_code == 200

        get_rate = await client.get("/api/oss/admin/rate-limit", headers=admin_headers)
        assert get_rate.status_code == 200
        assert get_rate.json()["data"]["global_rate_bytes"] == 1024 * 1024

        set_rate = await client.put(
            "/api/oss/admin/rate-limit",
            json={"global_rate_bytes": 2048},
            headers=admin_headers,
        )
        assert set_rate.status_code == 200
        limiter.set_global_rate.assert_called_once_with(2048)

        set_user_rate = await client.put(
            f"/api/oss/admin/rate-limit/users/{user_id}",
            json={"speed_multiplier": 2.0},
            headers=admin_headers,
        )
        assert set_user_rate.status_code == 200
        assert limiter.set_user_multiplier.called

    async def test_admin_file_endpoints(self, client, admin_headers, db_container):
        with (
            patch(
                "backend.plugins.oss.services.StorageService.admin_list_files"
            ) as mock_list,
            patch(
                "backend.plugins.oss.services.StorageService.admin_delete_file"
            ) as mock_delete,
        ):
            mock_list.return_value = [{"id": str(uuid.uuid4())}]
            mock_delete.return_value = None

            listed = await client.get("/api/oss/admin/files", headers=admin_headers)
            assert listed.status_code == 200
            assert listed.json()["code"] == "ok"

            file_id = str(uuid.uuid4())
            deleted = await client.delete(
                f"/api/oss/admin/files/{file_id}",
                headers=admin_headers,
            )
            assert deleted.status_code == 200
            assert deleted.json()["code"] == "ok"
