"""Middleware and unified error handling."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base error for application-level errors."""

    def __init__(self, message: str, code: str = "error", status_code: int = 400, data: dict | None = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.data = data or {}
        super().__init__(message)


class AuthError(AppError):
    def __init__(self, message: str = "未认证或认证已过期", code: str = "auth_error", status_code: int = 401):
        super().__init__(message, code, status_code)


class PermissionError(AppError):  # noqa: A001 — intentional shadow of builtin for domain clarity
    def __init__(self, message: str = "权限不足", code: str = "permission_denied", status_code: int = 403):
        super().__init__(message, code, status_code)


def error_response(message: str, code: str = "error", status_code: int = 400, data: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "data": data or {}},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return error_response(exc.message, exc.code, exc.status_code, exc.data)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        return error_response("内部服务器错误", "internal_error", status.HTTP_500_INTERNAL_SERVER_ERROR)


def setup_cors(app: FastAPI, origins: list[str]) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_current_user(request: Request) -> dict[str, Any] | None:
    """从 request.state 获取当前用户信息（由 auth 中间件注入）。"""
    return getattr(request.state, "user", None)


def require_user(request: Request) -> dict[str, Any]:
    """需要已认证用户，否则抛出 AuthError。"""
    user = get_current_user(request)
    if user is None:
        raise AuthError()
    return user


def require_level(min_level: int):
    """装饰器：要求用户等级 <= min_level（数字越小权限越高）。"""
    import functools

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if hasattr(arg, "headers") and hasattr(arg, "state"):
                        request = arg
                        break
            if request is None:
                raise AuthError("无法获取请求上下文")
            user = require_user(request)
            user_level = user.get("level", 5)
            if user_level > min_level:
                raise PermissionError(f"需要等级 <= {min_level}，当前等级 {user_level}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
