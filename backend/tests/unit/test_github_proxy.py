"""GitHub 代理插件 行为测试。

测试原则：
- 不关注内部实现细节
- 只验证公开方法的输入输出行为
- 用 mock 隔离外部依赖（网络、子进程）
"""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from backend.plugins.github_proxy.services import (
    GitHubService,
    GhCliService,
    HttpProxyService,
    GitHubProxyError,
)


# =============================================================================
# GhCliService 行为测试
# =============================================================================


class TestGhCliService:
    """测试 GitHub CLI 服务的行为。"""

    @pytest.mark.asyncio
    async def test_proxy_get_returns_parsed_json(self, fake_container):
        """GET 请求应返回解析后的 JSON 数据和状态码。"""
        service = GhCliService(fake_container)

        mock_response = json.dumps({"login": "testuser", "id": 123}).encode()

        with patch(
            "asyncio.create_subprocess_exec",
            return_value=mock_subprocess_success(mock_response),
        ):
            result = await service.proxy_request(
                method="GET",
                path="/user",
                query_params={},
                headers={},
                body=None,
                user_id="test",
            )

            assert result["status_code"] == 200
            assert result["data"]["login"] == "testuser"
            assert result["data"]["id"] == 123
            assert result["cached"] is True  # GET 请求应被缓存

    @pytest.mark.asyncio
    async def test_proxy_post_sends_body(self, fake_container):
        """POST 请求应把请求体传给 gh 命令。"""
        service = GhCliService(fake_container)

        mock_response = json.dumps({"id": 1, "name": "test-repo"}).encode()

        with patch(
            "asyncio.create_subprocess_exec",
            return_value=mock_subprocess_success(mock_response),
        ) as mock_exec:
            body = json.dumps({"name": "test-repo"}).encode()
            result = await service.proxy_request(
                method="POST",
                path="/user/repos",
                query_params={},
                headers={},
                body=body,
                user_id="test",
            )

            assert result["status_code"] == 200
            # 验证 gh 命令被正确调用
            mock_exec.assert_called_once()
            call_args = mock_exec.call_args[0]
            assert "POST" in call_args  # 方法正确
            assert "user/repos" in call_args  # 路径正确（前面的斜杠被去掉了）

    @pytest.mark.asyncio
    async def test_cli_not_installed_raises_error(self, fake_container):
        """gh 未安装时应抛出清晰的错误。"""
        service = GhCliService(fake_container)

        with patch(
            "asyncio.create_subprocess_exec",
            side_effect=FileNotFoundError("gh: not found"),
        ):
            with pytest.raises(GitHubProxyError) as excinfo:
                await service.proxy_request("GET", "/user", {}, {}, None, "test")

            assert "未找到 gh 命令" in str(excinfo.value)
            assert excinfo.value.code == "gh_not_installed"

    @pytest.mark.asyncio
    async def test_cli_timeout_raises_error(self, fake_container):
        """命令超时应抛出清晰的错误。"""
        service = GhCliService(fake_container)

        with patch(
            "asyncio.create_subprocess_exec",
            side_effect=TimeoutError("timeout"),
        ):
            with pytest.raises(GitHubProxyError) as excinfo:
                await service.proxy_request("GET", "/user", {}, {}, None, "test")

            assert "超时" in str(excinfo.value)


# =============================================================================
# HttpProxyService 行为测试
# =============================================================================


class TestHttpProxyService:
    """测试 HTTP 代理服务的行为。"""

    @pytest.mark.asyncio
    async def test_get_request_returns_json(self, fake_container):
        """GET 请求应返回 JSON 数据。"""
        service = HttpProxyService(fake_container)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser"}
        mock_response.headers = {"Content-Type": "application/json"}

        with patch.object(
            service._client,
            "request",
            return_value=mock_response,
        ):
            result = await service.proxy_request(
                method="GET",
                path="/user",
                query_params={},
                headers={},
                body=None,
                user_id="test",
            )

            assert result["status_code"] == 200
            assert result["data"]["login"] == "testuser"
            assert result["cached"] is True

    @pytest.mark.asyncio
    async def test_connect_error_raises_proxy_error(self, fake_container):
        """连接失败应抛出 GitHubProxyError。"""
        import httpx

        service = HttpProxyService(fake_container)

        with patch.object(
            service._client,
            "request",
            side_effect=httpx.ConnectError("connection failed"),
        ):
            with pytest.raises(GitHubProxyError) as excinfo:
                await service.proxy_request("GET", "/user", {}, {}, None, "test")

            assert "无法连接 GitHub" in str(excinfo.value)
            assert excinfo.value.code == "github_connect_error"


# =============================================================================
# GitHubService 自动降级 行为测试
# =============================================================================


class TestGitHubServiceAutoFallback:
    """测试统一门面的自动降级行为。"""

    @pytest.mark.asyncio
    async def test_http_success_no_fallback(self, fake_container):
        """HTTP 成功时，不降级，使用 HTTP 模式。"""
        service = GitHubService(fake_container)

        # Mock HTTP 成功
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"from": "http"}
        mock_response.headers = {}

        with patch.object(
            service.http_service._client, "request", return_value=mock_response
        ):
            result = await service.proxy_request(
                method="GET",
                path="/user",
                query_params={},
                headers={},
                body=None,
                user_id="test",
                mode="auto",
            )

            assert result["mode"] == "http"
            assert "fallback_from" not in result
            assert result["data"]["from"] == "http"

    @pytest.mark.asyncio
    async def test_http_failure_fallbacks_to_cli(self, fake_container):
        """HTTP 失败时，自动降级到 CLI 模式。"""
        service = GitHubService(fake_container)

        # Mock HTTP 失败
        import httpx

        with patch.object(
            service.http_service._client,
            "request",
            side_effect=httpx.ConnectError("failed"),
        ):
            # Mock CLI 成功
            mock_response = json.dumps({"from": "cli"}).encode()
            with patch(
                "asyncio.create_subprocess_exec",
                return_value=mock_subprocess_success(mock_response),
            ):
                result = await service.proxy_request(
                    method="GET",
                    path="/user",
                    query_params={},
                    headers={},
                    body=None,
                    user_id="test",
                    mode="auto",
                )

                assert result["mode"] == "cli"
                assert result["fallback_from"] == "http"
                assert result["data"]["from"] == "cli"

    @pytest.mark.asyncio
    async def test_cli_mode_skips_http(self, fake_container):
        """mode=cli 时，直接用 CLI，不尝试 HTTP。"""
        service = GitHubService(fake_container)

        mock_response = json.dumps({"from": "cli"}).encode()
        with patch(
            "asyncio.create_subprocess_exec",
            return_value=mock_subprocess_success(mock_response),
        ) as mock_exec:
            result = await service.proxy_request(
                method="GET",
                path="/user",
                query_params={},
                headers={},
                body=None,
                user_id="test",
                mode="cli",
            )

            assert result["mode"] == "cli"
            # HTTP 客户端不应被调用
            mock_exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_both_fail_raises_original_error(self, fake_container):
        """HTTP 和 CLI 都失败时，抛出原始错误。"""
        service = GitHubService(fake_container)

        import httpx

        with patch.object(
            service.http_service._client,
            "request",
            side_effect=httpx.ConnectError("http failed"),
        ):
            with patch(
                "asyncio.create_subprocess_exec",
                side_effect=FileNotFoundError("gh not found"),
            ):
                with pytest.raises(GitHubProxyError) as excinfo:
                    await service.proxy_request(
                        method="GET",
                        path="/user",
                        mode="auto",
                    )

                # 应该是 HTTP 的错误，因为是第一个失败的
                assert "http" in str(excinfo.value).lower()


# =============================================================================
# 缓存 行为测试
# =============================================================================


class TestCachingBehavior:
    """测试缓存行为。"""

    @pytest.mark.asyncio
    async def test_get_requests_are_cached(self, fake_container):
        """相同的 GET 请求第二次应命中缓存。"""
        service = GhCliService(fake_container)

        mock_response = json.dumps({"value": "first"}).encode()

        with patch(
            "asyncio.create_subprocess_exec",
            return_value=mock_subprocess_success(mock_response),
        ) as mock_exec:
            # 第一次调用
            result1 = await service.proxy_request("GET", "/user", {}, {}, None, "test")
            assert result1["cached"] is True  # 写入缓存了

            # 第二次调用
            result2 = await service.proxy_request("GET", "/user", {}, {}, None, "test")
            assert result2["cached"] is True  # 命中缓存

            # subprocess 应该只被调用了一次
            assert mock_exec.call_count == 1

    @pytest.mark.asyncio
    async def test_post_requests_are_not_cached(self, fake_container):
        """POST 请求不应该被缓存。"""
        service = GhCliService(fake_container)

        mock_response = json.dumps({"ok": True}).encode()

        with patch(
            "asyncio.create_subprocess_exec",
            return_value=mock_subprocess_success(mock_response),
        ) as mock_exec:
            await service.proxy_request("POST", "/user/repos", {}, {}, b"{}", "test")
            await service.proxy_request("POST", "/user/repos", {}, {}, b"{}", "test")

            # POST 应该每次都调用 subprocess
            assert mock_exec.call_count == 2

    @pytest.mark.asyncio
    async def test_clear_cache_removes_all_entries(self, fake_container):
        """clear_cache 应该清空所有缓存。"""
        service = GhCliService(fake_container)

        mock_response = json.dumps({"ok": True}).encode()

        with patch(
            "asyncio.create_subprocess_exec",
            return_value=mock_subprocess_success(mock_response),
        ) as mock_exec:
            # 填充缓存
            await service.proxy_request("GET", "/user", {}, {}, None, "test")
            assert mock_exec.call_count == 1

            # 命中缓存
            await service.proxy_request("GET", "/user", {}, {}, None, "test")
            assert mock_exec.call_count == 1

            # 清空缓存
            service.clear_cache()

            # 应该重新请求
            await service.proxy_request("GET", "/user", {}, {}, None, "test")
            assert mock_exec.call_count == 2


# =============================================================================
# 辅助函数
# =============================================================================


def mock_subprocess_success(stdout: bytes = b'{"ok": true}', stderr: bytes = b""):
    """创建成功的 subprocess mock。"""

    class MockProc:
        returncode = 0

        async def communicate(self, input=None):
            return stdout, stderr

        async def wait(self):
            return 0

    return MockProc()
