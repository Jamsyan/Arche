"""系统监控插件 —— 路由端点。"""

from __future__ import annotations

from fastapi import APIRouter, Query, Request

from backend.core.container import ServiceContainer
from backend.core.middleware import get_current_user, require_level, require_user

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/summary")
@require_level(0)
async def get_summary(request: Request):
    """系统概览（P0）。"""
    container: ServiceContainer = request.app.state.container
    svc = container.get("system_monitor")
    return {"code": "ok", "message": "获取成功", "data": svc.get_summary()}


@router.get("/cpu")
@require_level(0)
async def get_cpu(request: Request):
    """CPU 详情（P0）。"""
    container: ServiceContainer = request.app.state.container
    svc = container.get("system_monitor")
    return {"code": "ok", "message": "获取成功", "data": svc.get_cpu_detail()}


@router.get("/memory")
@require_level(0)
async def get_memory(request: Request):
    """内存详情（P0）。"""
    container: ServiceContainer = request.app.state.container
    svc = container.get("system_monitor")
    return {"code": "ok", "message": "获取成功", "data": svc.get_memory_detail()}


@router.get("/disk")
@require_level(0)
async def get_disk(request: Request):
    """磁盘详情（P0）。"""
    container: ServiceContainer = request.app.state.container
    svc = container.get("system_monitor")
    return {"code": "ok", "message": "获取成功", "data": svc.get_disk_detail()}


@router.get("/network")
@require_level(0)
async def get_network(request: Request):
    """网络 I/O（P0）。"""
    container: ServiceContainer = request.app.state.container
    svc = container.get("system_monitor")
    return {"code": "ok", "message": "获取成功", "data": svc.get_network_io()}


@router.get("/history")
@require_level(0)
async def get_history(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=300, description="每页数量"),
):
    """历史数据（P0）。"""
    container: ServiceContainer = request.app.state.container
    svc = container.get("system_monitor")
    return {
        "code": "ok",
        "message": "获取成功",
        "data": svc.get_history(page=page, page_size=page_size),
    }


@router.get("/processes")
@require_level(0)
async def get_processes(
    request: Request,
    sort_by: str = Query(
        "cpu_percent",
        description="排序字段：cpu_percent/memory_percent/pid/create_time",
    ),
    limit: int = Query(50, ge=1, le=200, description="返回数量上限"),
):
    """进程列表（P0）。"""
    container: ServiceContainer = request.app.state.container
    svc = container.get("system_monitor")
    return {
        "code": "ok",
        "message": "获取成功",
        "data": svc.get_processes(sort_by=sort_by, limit=limit),
    }


# ── 在线会话管理（P0） ──


@router.post("/online")
async def report_online(request: Request):
    """用户主动上报在线（登录时调用）。"""
    user = require_user(request)
    container: ServiceContainer = request.app.state.container
    if container.is_available("session_tracker"):
        tracker = container.get("session_tracker")
        tracker.user_online(user["id"], user["username"])
    return {"code": "ok", "message": "上线成功", "data": {}}


@router.post("/offline")
async def report_offline(request: Request):
    """用户主动上报离线（sendBeacon 或退出登录时调用）。"""
    user = get_current_user(request)
    if user:
        container: ServiceContainer = request.app.state.container
        if container.is_available("session_tracker"):
            tracker = container.get("session_tracker")
            tracker.user_offline(user["id"])
    return {"code": "ok", "message": "离线成功", "data": {}}


@router.get("/online")
@require_level(0)
async def get_online_users(request: Request):
    """获取在线用户列表（P0）。"""
    container: ServiceContainer = request.app.state.container
    if container.is_available("session_tracker"):
        tracker = container.get("session_tracker")
        return {
            "code": "ok",
            "message": "获取成功",
            "data": {
                "online_count": tracker.get_online_count(),
                "users": tracker.get_online_users(),
                "stats": tracker.get_stats(),
            },
        }
    return {"code": "ok", "message": "获取成功", "data": {"online_count": 0, "users": [], "stats": {}}}


# ── Dashboard 聚合端点（P0） ──


@router.get("/dashboard")
@require_level(0)
async def get_dashboard(request: Request):
    """控制台首页聚合数据（P0），一次调用拿全。"""
    container: ServiceContainer = request.app.state.container

    data: dict = {}

    # 1. 系统概览
    if container.is_available("system_monitor"):
        sys_svc = container.get("system_monitor")
        data["system"] = sys_svc.get_summary()

    # 2. 在线统计
    if container.is_available("session_tracker"):
        tracker = container.get("session_tracker")
        data["online"] = tracker.get_stats()

    # 3. API 请求统计
    if container.is_available("request_stats"):
        stats = container.get("request_stats")
        data["requests"] = stats.get_stats()
        data["qps_history"] = stats.get_qps_history()

    # 4. 博客统计（帖子总数、PV 总数等）
    if container.is_available("blog"):
        blog_svc = container.get("blog")
        try:
            data["blog"] = await blog_svc.get_stats()
        except Exception:
            data["blog"] = {}

    return {"code": "ok", "message": "获取成功", "data": data}
