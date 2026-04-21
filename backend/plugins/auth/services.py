"""Auth plugin — 用户认证服务：CRUD、密码验证、JWT 签发/验证。"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import func, select

from backend.core.middleware import AppError, AuthError


class AuthService:
    """认证服务：用户注册/登录/登出/token 管理。"""

    def __init__(self, container):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]
        self.secret_key = container.get("config").get_required("SECRET_KEY")
        # token 有效期：access_token 2 小时，refresh_token 7 天
        self.access_token_expire_hours = 2
        self.refresh_token_expire_days = 7

    # --- 用户注册 ---
    async def register(self, username: str, password: str, level: int = 5) -> dict:
        """注册新用户。第一个注册用户自动成为 P0（最高权限），后续默认 P5。"""
        from backend.plugins.auth.models import User

        async with self.session_factory() as session:
            # 检查用户名是否已存在
            result = await session.execute(
                select(User).where(User.username == username)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise AppError("用户名已存在", code="username_exists", status_code=409)

            # 第一个注册用户自动成为 P0
            count_result = await session.execute(select(func.count(User.id)))
            is_first_user = count_result.scalar() == 0
            effective_level = 0 if is_first_user else level

            # 密码 hash
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            user = User(
                username=username,
                password_hash=password_hash,
                level=effective_level,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            # 签发 token
            access_token = self._create_token(user, expires_hours=self.access_token_expire_hours)
            refresh_token = self._create_token(user, expires_days=self.refresh_token_expire_days)

            return {
                "user": self._user_to_dict(user),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

    # --- 用户登录 ---
    async def login(self, username: str, password: str) -> dict:
        """验证用户名密码，返回 JWT token。"""
        from backend.plugins.auth.models import User

        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise AuthError("用户名或密码错误")

            # 验证密码
            if not bcrypt.checkpw(
                password.encode("utf-8"), user.password_hash.encode("utf-8")
            ):
                raise AuthError("用户名或密码错误")

            access_token = self._create_token(user, expires_hours=self.access_token_expire_hours)
            refresh_token = self._create_token(user, expires_days=self.refresh_token_expire_days)

            return {
                "user": self._user_to_dict(user),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

    # --- 登出 ---
    async def logout(self, token: str) -> None:
        """登出。当前版本无 token 黑名单机制，登出由客户端清除本地 token 实现。"""
        # 后续可接入 Redis 实现 token 黑名单
        pass

    # --- 获取当前用户 ---
    async def get_user_by_id(self, user_id: uuid.UUID) -> dict | None:
        """根据 ID 获取用户信息。"""
        from backend.plugins.auth.models import User

        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                return self._user_to_dict(user)
            return None

    # --- Token 刷新 ---
    async def refresh_token(self, refresh_token: str) -> dict:
        """使用 refresh token 换取新的 access token。"""
        payload = self._verify_token(refresh_token)
        user_id = uuid.UUID(payload["sub"])

        user = await self.get_user_by_id(user_id)
        if not user:
            raise AuthError("用户不存在")

        # 从 payload 构造用户数据用于签发新 token
        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=self.access_token_expire_hours)
        new_payload = {
            "sub": user["id"],
            "level": user["level"],
            "blog_quality_level": user["blog_quality_level"],
            "exp": exp,
        }
        new_access_token = jwt.encode(new_payload, self.secret_key, algorithm="HS256")
        return {"access_token": new_access_token}

    # --- JWT 内部方法 ---
    def _create_token(self, user, expires_hours: int | None = None, expires_days: int | None = None) -> str:
        """签发 JWT token。"""
        now = datetime.now(timezone.utc)
        if expires_hours is not None:
            exp = now + timedelta(hours=expires_hours)
        elif expires_days is not None:
            exp = now + timedelta(days=expires_days)
        else:
            exp = now + timedelta(hours=self.access_token_expire_hours)

        payload = {
            "sub": str(user.id),
            "username": user.username,
            "level": user.level,
            "blog_quality_level": user.blog_quality_level,
            "exp": exp,
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def _verify_token(self, token: str) -> dict:
        """验证并解析 JWT token。"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthError("Token 已过期")
        except jwt.InvalidTokenError:
            raise AuthError("无效 Token")

    # --- 工具方法 ---
    def _user_to_dict(self, user) -> dict:
        """将 User 对象转为字典（用于返回）。"""
        return {
            "id": str(user.id),
            "username": user.username,
            "level": user.level,
            "blog_quality_level": user.blog_quality_level,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
