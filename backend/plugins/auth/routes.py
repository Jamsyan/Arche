"""Auth plugin — 路由：注册、登录、登出、获取当前用户、刷新 token。"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, Request

from backend.core.container import ServiceContainer
from backend.core.middleware import require_user


router = APIRouter(prefix="/api/auth", tags=["auth"])


# --- 请求体模型 ---
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


# --- 路由 ---
@router.post("/register")
async def register(req: RegisterRequest, request: Request):
    """用户注册，默认 P5 等级。"""
    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    result = await auth_service.register(
        username=req.username,
        password=req.password,
    )
    return {"code": "ok", "message": "注册成功", "data": result}


@router.post("/login")
async def login(req: LoginRequest, request: Request):
    """用户登录，返回 JWT token。"""
    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    result = await auth_service.login(
        username=req.username,
        password=req.password,
    )
    return {"code": "ok", "message": "登录成功", "data": result}


@router.post("/logout")
async def logout(request: Request):
    """用户登出。"""
    user = require_user(request)
    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
    await auth_service.logout(token)
    return {"code": "ok", "message": "登出成功", "data": {}}


@router.get("/me")
async def get_me(request: Request):
    """获取当前登录用户信息。"""
    user = require_user(request)
    return {"code": "ok", "message": "获取成功", "data": user}


@router.post("/refresh")
async def refresh(req: RefreshRequest, request: Request):
    """刷新 access token。"""
    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    result = await auth_service.refresh_token(req.refresh_token)
    return {"code": "ok", "message": "刷新成功", "data": result}
