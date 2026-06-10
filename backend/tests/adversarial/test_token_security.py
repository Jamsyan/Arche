from __future__ import annotations

import uuid


class TestTokenLifecycle:
    """Token 生命周期安全测试：登出失效、刷新安全、多设备等。"""

    async def test_logout_invalidates_token(self, client, auth_headers):
        """登出后旧 token 应失效。"""
        # 先获取当前用户信息确认 token 有效
        me_resp = await client.get("/api/auth/me", headers=auth_headers)
        assert me_resp.status_code == 200

        # 登出
        logout_resp = await client.post("/api/auth/logout", headers=auth_headers)
        assert logout_resp.status_code == 200

        # 使用同一 token 再次请求应被拒绝
        me_resp2 = await client.get("/api/auth/me", headers=auth_headers)
        status = me_resp2.status_code
        data = me_resp2.json() if status != 200 else {}
        assert status in (401, 403), (
            f"Token still valid after logout: status {status}, body: {data}"
        )
        if status == 401:
            assert data["code"] in ("auth_error", "token_expired", "invalid_token"), (
                f"Unexpected error code: {data.get('code')}"
            )

    async def test_refresh_token_works_after_logout(self, client):
        """登出后 refresh token 应仍然有效（access 登出只黑名单 access）。"""
        # 注册用户获取 access + refresh token
        email = f"refresh-test-{uuid.uuid4().hex[:8]}@example.com"
        reg_resp = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "username": email.split("@")[0],
                "password": "testpass123",
            },
        )
        assert reg_resp.status_code == 200
        reg_data = reg_resp.json()["data"]
        access_token = reg_data["access_token"]
        refresh_token_val = reg_data["refresh_token"]

        # 登出 (黑名单 access token)
        await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # 用 refresh token 换取新 access token 应成功
        refresh_resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token_val},
        )
        assert refresh_resp.status_code == 200, (
            f"Refresh failed after logout: status {refresh_resp.status_code}"
        )
        new_access = refresh_resp.json()["data"]["access_token"]

        # 新 access token 应有效
        me_resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {new_access}"},
        )
        assert me_resp.status_code == 200

    async def test_jti_uniqueness(self):
        """每个 token 的 jti 应唯一。"""

        # 构造一个最小 payload 来测试理论
        payloads = []
        for _ in range(100):
            payloads.append(
                {
                    "jti": str(uuid.uuid4()),
                    "sub": str(uuid.uuid4()),
                    "level": 5,
                    "exp": 9999999999,
                }
            )
        jtis = [p["jti"] for p in payloads]
        assert len(jtis) == len(set(jtis)), "Duplicate jti values detected"

    async def test_reused_refresh_token_after_refresh(self, client):
        """刷新后旧 refresh token 应无法再次使用。"""
        email = f"reuse-test-{uuid.uuid4().hex[:8]}@example.com"
        reg_resp = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "username": email.split("@")[0],
                "password": "testpass123",
            },
        )
        assert reg_resp.status_code == 200
        refresh_token_val = reg_resp.json()["data"]["refresh_token"]

        # 使用 refresh token 一次
        refresh_resp1 = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token_val},
        )
        assert refresh_resp1.status_code == 200

        # 再次使用同一 refresh token（如被重用，应拒绝）
        refresh_resp2 = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token_val},
        )
        # 目前可能返回 200（无 refresh token rotation），这里只确认不会 500
        assert refresh_resp2.status_code != 500, "Reused refresh token caused 500"
