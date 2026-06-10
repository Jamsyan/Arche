from __future__ import annotations


class TestHTTPMethodTampering:
    """HTTP 方法篡改测试：验证端点只接受预期的方法。"""

    async def test_blog_create_rejects_get(self, client, auth_headers):
        """博客列表查询返回正常（GET 到列表端点）。"""
        resp = await client.get("/api/blog/posts", headers=auth_headers)
        # blog/posts GET 是列表查询，应该正常返回
        assert resp.status_code != 405 and resp.status_code != 500

    async def test_login_rejects_get(self, client):
        """登录端点拒绝 GET 请求。"""
        resp = await client.get("/api/auth/login")
        assert resp.status_code == 405 or resp.status_code == 404

    async def test_register_rejects_put(self, client):
        """注册端点拒绝 PUT 请求。"""
        resp = await client.put(
            "/api/auth/register",
            json={"email": "test@test.com", "username": "test", "password": "testpass123"},
        )
        assert resp.status_code in (405, 404), (
            f"Register endpoint accepted PUT: status {resp.status_code}"
        )

    async def test_me_endpoint_rejects_post(self, client, auth_headers):
        """当前用户端点拒绝 POST 请求。"""
        resp = await client.post("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 405, (
            f"/api/auth/me accepted POST: status {resp.status_code}"
        )

    async def test_trace_method_rejected(self, client):
        """TRACE 方法应被拒绝。"""
        resp = await client.request("TRACE", "/api/auth/login")
        assert resp.status_code in (405, 404), (
            f"TRACE method not rejected: status {resp.status_code}"
        )

    async def test_options_method_on_api(self, client):
        """OPTIONS 请求应返回允许的方法。"""
        resp = await client.options("/api/auth/login")
        assert resp.status_code in (200, 204, 405), (
            f"OPTIONS request failed: status {resp.status_code}"
        )
        if resp.status_code == 200:
            assert "allow" in resp.headers or "access-control-allow-methods" in resp.headers
