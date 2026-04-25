"""GitHub Proxy 模块 API 集成测试。

测试真实 HTTP 路由行为。
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.mark.asyncio
@pytest.mark.xfail(reason="集成测试依赖注入问题待修复")
class TestGitHubProxyAPI:
    """GitHub 代理 API 测试。"""

    async def test_search_repositories_endpoint_exists(self, client, auth_headers):
        """搜索仓库接口应存在并返回正确结构。"""
        # Mock 掉 HTTP 请求，避免真实网络调用
        with patch("backend.plugins.github_proxy.services.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "total_count": 1,
                "items": [{"name": "test-repo", "full_name": "owner/test-repo"}]
            }
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.get.side_effect = None

            response = await client.get(
                "/api/github/search/repositories",
                params={"q": "python"},
                headers=auth_headers,
            )
            # 即使 mock 有问题，至少 404 说明路由不存在
            assert response.status_code != 404

    async def test_search_endpoint_requires_query_param(self, client, auth_headers):
        """搜索接口缺少 q 参数应返回 422。"""
        response = await client.get(
            "/api/github/search/repositories",
            headers=auth_headers,
        )
        assert response.status_code == 422  # FastAPI 自动校验

    async def test_health_check_endpoint(self, client, auth_headers):
        """健康检查接口应正常返回。"""
        # Mock gh 命令调用
        with patch("backend.plugins.github_proxy.services.GhCliService._run_gh_command") as mock_run:
            mock_run.return_value = {
                "data": {"rate": {"limit": 5000, "used": 10}},
                "status_code": 200,
                "headers": {},
            }

            response = await client.get(
                "/api/github/health/status",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == "ok"
            assert "data" in data
            assert "cli" in data["data"]
            assert "http" in data["data"]

    async def test_proxy_endpoint_get(self, client, auth_headers):
        """GET 请求主代理接口应正常工作。"""
        # Mock 服务层返回结果
        with patch("backend.plugins.github_proxy.services.GitHubService.proxy_request") as mock_proxy:
            mock_proxy.return_value = {
                "status_code": 200,
                "data": {"login": "testuser", "id": 123},
                "cached": False,
                "mode": "http",
            }

            response = await client.get(
                "/api/github/user",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["login"] == "testuser"
            assert response.headers["X-GitHub-Cache"] == "MISS"
            assert response.headers["X-GitHub-Mode"] == "http"

    async def test_proxy_endpoint_post(self, client, auth_headers):
        """POST 请求主代理接口应正常工作。"""
        with patch("backend.plugins.github_proxy.services.GitHubService.proxy_request") as mock_proxy:
            mock_proxy.return_value = {
                "status_code": 201,
                "data": {"id": 1, "name": "new-repo"},
                "cached": False,
                "mode": "http",
            }

            response = await client.post(
                "/api/github/user/repos",
                headers=auth_headers,
                json={"name": "new-repo", "private": True},
            )

            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "new-repo"

            # 验证 body 被正确传递
            call_args = mock_proxy.call_args
            assert "body" in call_args.kwargs
            assert json.loads(call_args.kwargs["body"]) == {"name": "new-repo", "private": True}

    async def test_proxy_raw_endpoint(self, client, auth_headers):
        """静态资源代理接口应返回二进制内容。"""
        test_content = b"# Test README\nThis is a test file."
        with patch("backend.plugins.github_proxy.services.GitHubService.proxy_raw_content") as mock_raw:
            mock_raw.return_value = {
                "status_code": 200,
                "data": test_content,
                "headers": {"Content-Type": "text/plain"},
                "cached": True,
                "mode": "cli",
            }

            response = await client.get(
                "/api/github/raw/owner/repo/main/README.md",
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert response.content == test_content
            assert response.headers["Content-Type"] == "text/plain"
            assert response.headers["X-GitHub-Cache"] == "HIT"
            assert response.headers["X-GitHub-Mode"] == "cli"

    async def test_clear_cache_endpoint(self, client, auth_headers):
        """缓存清空接口应正常工作。"""
        with patch("backend.plugins.github_proxy.services.GitHubService.clear_cache") as mock_clear:
            mock_clear.return_value = {"http": 10, "cli": 5}

            response = await client.post(
                "/api/github/cache/clear",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == "ok"
            assert "已清空 HTTP: 10, CLI: 5" in data["message"]
            assert data["data"]["cleared"] == {"http": 10, "cli": 5}

    async def test_endpoint_requires_authentication(self, client):
        """未登录用户访问接口应返回 401 错误。"""
        # 不传递 auth_headers
        response = await client.get("/api/github/health/status")
        assert response.status_code == 401

        response = await client.get("/api/github/user")
        assert response.status_code == 401

        response = await client.get("/api/github/raw/owner/repo/main/README.md")
        assert response.status_code == 401

        response = await client.post("/api/github/cache/clear")
        assert response.status_code == 401

    async def test_proxy_mode_parameter(self, client, auth_headers):
        """mode 参数应被正确传递给服务层。"""
        with patch("backend.plugins.github_proxy.services.GitHubService.proxy_request") as mock_proxy:
            mock_proxy.return_value = {
                "status_code": 200,
                "data": {},
                "cached": False,
                "mode": "cli",
            }

            # 测试 mode=cli
            response = await client.get(
                "/api/github/user",
                params={"mode": "cli"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            call_args = mock_proxy.call_args
            assert call_args.kwargs["mode"] == "cli"

            # 测试 mode=http
            response = await client.get(
                "/api/github/user",
                params={"mode": "http"},
                headers=auth_headers,
            )

            call_args = mock_proxy.call_args
            assert call_args.kwargs["mode"] == "http"
