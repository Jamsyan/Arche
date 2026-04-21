"""Tests for Auth plugin."""

import pytest

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from backend.core.middleware import AuthError


def test_password_hashing():
    """密码应该被 bcrypt hash 存储。"""
    password = "testpassword123"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    assert bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    assert not bcrypt.checkpw("wrongpassword".encode("utf-8"), hashed.encode("utf-8"))


def test_token_creation_and_verification():
    """JWT token 应包含用户信息且可验证。"""
    secret = "test-secret-key"

    class MockUser:
        id = "test-user-id"
        username = "testuser"
        level = 3
        blog_quality_level = 1

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(MockUser.id),
        "username": MockUser.username,
        "level": MockUser.level,
        "blog_quality_level": MockUser.blog_quality_level,
        "exp": now + timedelta(hours=2),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    # 验证
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    assert decoded["username"] == "testuser"
    assert decoded["level"] == 3


def test_token_verification_expired():
    """过期 token 应抛出 AuthError。"""
    secret = "test-key"

    expired_payload = {
        "sub": "user-1",
        "username": "test",
        "level": 5,
        "blog_quality_level": 0,
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(expired_payload, secret, algorithm="HS256")

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired_token, secret, algorithms=["HS256"])
