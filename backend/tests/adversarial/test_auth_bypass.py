from __future__ import annotations

from backend.tests.adversarial.conftest import SQLI_PAYLOADS


class TestAuthBypass:
    async def test_empty_password_rejected(self, client):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "empty@test.com", "username": "emptytest", "password": ""},
        )
        assert resp.status_code == 422

    async def test_single_char_password_rejected(self, client):
        resp = await client.post(
            "/api/auth/register",
            json={"email": "short@test.com", "username": "shorttest", "password": "a"},
        )
        assert resp.status_code == 422

    async def test_oversized_password_rejected(self, client):
        long_password = "x" * 1000
        resp = await client.post(
            "/api/auth/register",
            json={
                "email": "long@test.com",
                "username": "longtest",
                "password": long_password,
            },
        )
        assert resp.status_code == 422

    async def test_sqli_in_login_identity_rejected(self, client):
        for payload in SQLI_PAYLOADS:
            resp = await client.post(
                "/api/auth/login",
                json={"identity": payload, "password": "anypass"},
            )
            assert resp.status_code == 401, (
                f"SQLi login payload not rejected: {payload}"
            )
            data = resp.json()
            assert data["code"] == "auth_error"

    async def test_regular_user_cannot_access_admin_endpoints(
        self, client, auth_headers
    ):
        resp = await client.get("/api/auth/users", headers=auth_headers)
        assert resp.status_code == 403
        data = resp.json()
        assert data["code"] == "permission_denied"

        resp = await client.post(
            "/api/admin/config",
            json={"key": "test", "value": "test"},
            headers=auth_headers,
        )
        assert resp.status_code == 403
        data = resp.json()
        assert data["code"] == "permission_denied"

    async def test_no_auth_header_rejected(self, client):
        resp = await client.get("/api/auth/users")
        assert resp.status_code == 401

        resp = await client.get("/api/oss/my")
        assert resp.status_code == 401

    async def test_malformed_token_rejected(self, client):
        cases = [
            ("Bearer invalid", "invalid_token"),
            ("Bearer ", "invalid_token"),
            ("not-a-bearer", "auth_error"),
        ]
        for header_value, expected_code in cases:
            resp = await client.get(
                "/api/auth/me",
                headers={"Authorization": header_value},
            )
            assert resp.status_code == 401
            data = resp.json()
            assert data["code"] == expected_code

    async def test_admin_can_access_admin_endpoints(self, client, admin_headers):
        resp = await client.get("/api/auth/users", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == "ok"
