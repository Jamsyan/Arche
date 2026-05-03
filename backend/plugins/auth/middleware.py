"""认证插件 —— JWT 认证中间件。

从请求头提取 Bearer token，解析后注入 request.state.user。
对公开路由（/api/auth/register, /api/auth/login）跳过认证。
"""

from __future__ import annotations

import jwt

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT 认证中间件：解析 token 并注入 request.state.user。"""

    # 不需要认证的公开路由
    PUBLIC_PATHS = {
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/refresh",
        # 博客公开路由
        "/api/blog/posts",
        "/api/blog/tags",
    }

    # 博客公开 GET 路由前缀（所有博客 GET 端点都是公开浏览）
    BLOG_PUBLIC_PREFIXES = (
        "/api/blog/posts/",
        "/api/blog/tags/",
    )

    # FastAPI 内置路由（/docs, /openapi.json 等）跳过认证
    INTERNAL_PREFIXES = ("/docs", "/openapi.json", "/redoc")

    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        method = request.method

        # 公开路由和 FastAPI 内置路由直接放行
        if path in self.PUBLIC_PATHS or path.startswith(self.INTERNAL_PREFIXES):
            return await call_next(request)

        # 博客公开 GET 路由放行（限定具体前缀，避免放行 moderation 等管理端点）
        if method == "GET" and path.startswith(self.BLOG_PUBLIC_PREFIXES):
            return await call_next(request)

        # 提取 Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"code": "auth_error", "message": "缺少认证信息", "data": {}},
            )

        token = auth_header[7:]  # 去掉 "Bearer " 前缀

        # 解析 token
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={
                    "code": "token_expired",
                    "message": "Token 已过期",
                    "data": {},
                },
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"code": "invalid_token", "message": "无效 Token", "data": {}},
            )

        # 注入用户信息到 request.state
        request.state.user = {
            "id": payload["sub"],
            "email": payload.get("email", ""),
            "username": payload.get("username", ""),
            "level": payload["level"],
            "blog_quality_level": payload.get("blog_quality_level", 0),
        }

        return await call_next(request)
