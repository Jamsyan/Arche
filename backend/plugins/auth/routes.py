"""Auth plugin — 路由：注册、登录、登出、获取当前用户、刷新 token。"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, Query, Request

from backend.core.container import ServiceContainer
from backend.core.middleware import require_level, require_user


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


# --- 管理端点（P0） ---
class UpdateUserRequest(BaseModel):
    level: int | None = Field(None, ge=0, le=10, description="用户等级")
    is_active: bool | None = Field(None, description="是否启用")


@router.get("/users")
@require_level(0)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: str | None = Query(None, description="状态过滤：active/disabled"),
):
    """用户列表（P0）。"""
    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    result = await auth_service.list_users(page=page, page_size=page_size, status_filter=status)
    return {"code": "ok", "message": "获取成功", "data": result}


@router.get("/users/{user_id}")
@require_level(0)
async def get_user(user_id: str, request: Request):
    """用户详情（P0）。"""
    import uuid

    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    result = await auth_service.get_user(uuid.UUID(user_id))
    if not result:
        return {"code": "not_found", "message": "用户不存在", "data": None}
    return {"code": "ok", "message": "获取成功", "data": result}


@router.put("/users/{user_id}")
@require_level(0)
async def update_user(user_id: str, req: UpdateUserRequest, request: Request):
    """修改用户等级/状态（P0）。"""
    import uuid

    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    result = await auth_service.update_user(
        uuid.UUID(user_id), level=req.level, is_active=req.is_active
    )
    return {"code": "ok", "message": "修改成功", "data": result}


@router.delete("/users/{user_id}")
@require_level(0)
async def delete_user(user_id: str, request: Request):
    """禁用用户（P0）。"""
    import uuid

    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    await auth_service.disable_user(uuid.UUID(user_id))
    return {"code": "ok", "message": "用户已禁用", "data": {}}


@router.post("/users/{user_id}/disable")
@require_level(0)
async def disable_user(user_id: str, request: Request):
    """禁用用户（P0）。不能禁用自己。"""
    import uuid

    current_user = require_user(request)
    if str(current_user["id"]) == user_id:
        return {"code": "forbidden", "message": "不能禁用自己", "data": {}}

    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    result = await auth_service.disable_user(uuid.UUID(user_id))
    return {"code": "ok", "message": "用户已禁用", "data": result}


@router.post("/users/{user_id}/enable")
@require_level(0)
async def enable_user(user_id: str, request: Request):
    """启用用户（P0）。"""
    import uuid

    container: ServiceContainer = request.app.state.container
    auth_service = container.get("auth")
    result = await auth_service.enable_user(uuid.UUID(user_id))
    return {"code": "ok", "message": "用户已启用", "data": result}
