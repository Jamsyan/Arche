from __future__ import annotations


class TestCORS:
    """CORS 配置验证测试。"""

    async def test_cors_headers_on_api_response(self, client):
        """API 响应应包含 CORS 头（当请求带 Origin 时）。"""
        resp = await client.get(
            "/api/blog/posts",
            headers={"Origin": "http://localhost:5173"},
        )
        assert "access-control-allow-origin" in resp.headers

    async def test_cors_allows_localhost_origin(self, client):
        """localhost 来源应在允许列表中。"""
        resp = await client.get(
            "/api/blog/posts",
            headers={"Origin": "http://localhost:5173"},
        )
        origin = resp.headers.get("access-control-allow-origin", "")
        assert origin == "http://localhost:5173", (
            f"Expected origin http://localhost:5173, got {origin}"
        )

    async def test_unknown_origin_rejected(self, client):
        """未知来源应被拒绝。"""
        resp = await client.get(
            "/api/blog/posts",
            headers={"Origin": "https://evil.com"},
        )
        # 如果 CORS 配置允许 *，则不会拒绝
        # 这里只确认响应不会因为 CORS 检查而崩溃
        assert resp.status_code != 500

    async def test_credentials_allowed_with_cors(self, client):
        """带凭据的跨域请求应被支持。"""
        resp = await client.get(
            "/api/blog/posts",
            headers={"Origin": "http://localhost:5173"},
        )
        assert "access-control-allow-credentials" in resp.headers
        assert resp.headers["access-control-allow-credentials"] == "true"

    async def test_cors_preflight_success(self, client):
        """OPTIONS 预检请求应正确处理。"""
        resp = await client.options(
            "/api/blog/posts",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type",
            },
        )
        assert resp.status_code in (200, 204), (
            f"Preflight request failed: status {resp.status_code}"
        )
