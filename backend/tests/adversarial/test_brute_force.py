from __future__ import annotations


class TestBruteForceProtection:
    """验证登录暴力破解防护机制（限流 + 弱密码拒绝）。"""

    async def test_consecutive_failed_logins_rate_limited(self, client):
        """连续多次错误登录后应被限流。"""
        payload = {"identity": "brute-force-test@example.com", "password": "wrongpass"}
        responses = []
        for _ in range(10):
            resp = await client.post("/api/auth/login", json=payload)
            responses.append(resp.status_code)

        # 至少有一次返回 429（限流）
        rate_limited = [s for s in responses if s == 429]
        assert len(rate_limited) >= 1, (
            f"No 429 response received after repeated login attempts. "
            f"Got statuses: {responses}"
        )

    async def test_rate_limit_resets_after_successful_login(self, client, unique_email):
        """登录成功后限流计数应重置。"""
        # 先注册一个用户
        register_resp = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "username": unique_email.split("@")[0],
                "password": "testpass123",
                "nickname": "testuser",
            },
        )
        assert register_resp.status_code == 200

        # 连续 4 次错误登录（接近限流阈值 5）
        for _ in range(4):
            await client.post(
                "/api/auth/login",
                json={"identity": unique_email, "password": "wrongpass"},
            )

        # 正确登录应成功（重置计数）
        login_resp = await client.post(
            "/api/auth/login",
            json={"identity": unique_email, "password": "testpass123"},
        )
        assert login_resp.status_code == 200, (
            f"Successful login after 4 failures was rejected: "
            f"status {login_resp.status_code}"
        )

    async def test_empty_password_rejected(self, client):
        resp = await client.post(
            "/api/auth/register",
            json={
                "email": "empty-pass@test.com",
                "username": "emptypasstest",
                "password": "",
                "nickname": "testuser",
            },
        )
        assert resp.status_code == 422

    async def test_single_char_password_rejected(self, client):
        resp = await client.post(
            "/api/auth/register",
            json={
                "email": "short-pass@test.com",
                "username": "shortpasstest",
                "password": "a",
                "nickname": "testuser",
            },
        )
        assert resp.status_code == 422

    async def test_oversized_password_rejected(self, client):
        long_password = "x" * 1000
        resp = await client.post(
            "/api/auth/register",
            json={
                "email": "long-pass@test.com",
                "username": "longpasstest",
                "password": long_password,
                "nickname": "testuser",
            },
        )
        assert resp.status_code == 422
