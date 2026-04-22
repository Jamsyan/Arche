"""System Monitor plugin — 路由端点。"""

from __future__ import annotations

from fastapi import APIRouter, Query, Request

from backend.core.container import ServiceContainer
from backend.core.middleware import require_level

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
