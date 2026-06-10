from __future__ import annotations

EXPECTED_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "x-xss-protection": "1; mode=block",
    "referrer-policy": "strict-origin-when-cross-origin",
}


class TestSecurityHeaders:
    """验证所有 API 响应是否包含必要的安全响应头。"""

    async def test_login_response_has_security_headers(self, client):
        resp = await client.post(
            "/api/auth/login",
            json={"identity": "nonexistent", "password": "any"},
        )
        for header, expected_value in EXPECTED_HEADERS.items():
            assert header in resp.headers, f"Missing security header: {header}"
            assert resp.headers[header] == expected_value, (
                f"Security header {header} value mismatch: "
                f"expected {expected_value!r}, got {resp.headers[header]!r}"
            )

    async def test_register_response_has_security_headers(self, client):
        resp = await client.post(
            "/api/auth/register",
            json={
                "email": "headers-test@example.com",
                "username": "headerstest",
                "password": "testpass123",
            },
        )
        for header, expected_value in EXPECTED_HEADERS.items():
            assert header in resp.headers, f"Missing security header: {header}"
            assert resp.headers[header] == expected_value

    async def test_public_get_response_has_security_headers(self, client):
        resp = await client.get("/api/blog/posts")
        for header, expected_value in EXPECTED_HEADERS.items():
            assert header in resp.headers, f"Missing security header: {header}"
            assert resp.headers[header] == expected_value

    async def test_error_response_has_security_headers(self, client, auth_headers):
        resp = await client.get("/api/auth/users", headers=auth_headers)
        for header, expected_value in EXPECTED_HEADERS.items():
            assert header in resp.headers, f"Missing security header: {header}"
            assert resp.headers[header] == expected_value

    async def test_permissions_policy_header_exists(self, client):
        resp = await client.get("/api/blog/posts")
        assert "permissions-policy" in resp.headers, "Missing Permissions-Policy header"
        policy = resp.headers["permissions-policy"]
        assert "camera=()" in policy
        assert "microphone=()" in policy
        assert "geolocation=()" in policy
