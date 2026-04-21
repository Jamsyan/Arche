"""Cloud Integration plugin — API 路由。"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from fastapi import APIRouter, Query, Request

from backend.core.container import ServiceContainer
from backend.core.middleware import require_level, require_user


router = APIRouter(prefix="/api/cloud", tags=["cloud"])


# --- 请求体模型 ---
class CreateJobRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=256, description="任务名称")
    config: dict = Field(..., description="模型配置（JSON）")


class CreateInstanceRequest(BaseModel):
    instance_name: str = Field(..., min_length=1, max_length=256, description="实例名称")
    gpu_type: str = Field(..., min_length=1, max_length=64, description="GPU 类型")


# --- 任务 CRUD（P0） ---
@router.get("/jobs")
@require_level(0)
async def list_jobs(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: str | None = Query(None, description="状态过滤"),
):
    """训练任务列表（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.list_jobs(
        page=page,
        page_size=page_size,
        status_filter=status,
    )
    return {"code": "ok", "message": "获取成功", "data": result}


@router.get("/jobs/{job_id}")
@require_level(0)
async def get_job(job_id: str, request: Request):
    """训练任务详情（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.get_job(uuid.UUID(job_id))
    return {"code": "ok", "message": "获取成功", "data": result}


@router.post("/jobs")
@require_level(0)
async def create_job(req: CreateJobRequest, request: Request):
    """创建训练任务（P0）。"""
    user = require_user(request)
    creator_id = uuid.UUID(user["id"])

    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.create_job(
        creator_id=creator_id,
        name=req.name,
        config=req.config,
    )
    return {"code": "ok", "message": "创建成功", "data": result}


@router.delete("/jobs/{job_id}")
@require_level(0)
async def delete_job(job_id: str, request: Request):
    """删除训练任务（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    await service.delete_job(uuid.UUID(job_id))
    return {"code": "ok", "message": "删除成功", "data": {}}


# --- 任务状态操作（P0） ---
@router.post("/jobs/{job_id}/start")
@require_level(0)
async def start_job(job_id: str, request: Request):
    """启动训练任务（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.start_job(uuid.UUID(job_id))
    return {"code": "ok", "message": "启动成功", "data": result}


@router.post("/jobs/{job_id}/stop")
@require_level(0)
async def stop_job(job_id: str, request: Request):
    """停止训练任务（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.stop_job(uuid.UUID(job_id))
    return {"code": "ok", "message": "停止成功", "data": result}


@router.post("/jobs/{job_id}/complete")
@require_level(0)
async def complete_job(
    job_id: str,
    request: Request,
    result_path: str | None = Query(None, description="结果路径"),
):
    """标记任务完成（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.complete_job(uuid.UUID(job_id), result_path=result_path)
    return {"code": "ok", "message": "标记完成", "data": result}


@router.post("/jobs/{job_id}/fail")
@require_level(0)
async def fail_job(
    job_id: str,
    request: Request,
    error_message: str = Query(..., description="错误信息"),
):
    """标记任务失败（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.fail_job(uuid.UUID(job_id), error_message=error_message)
    return {"code": "ok", "message": "标记失败", "data": result}


# --- 训练日志（P0） ---
@router.get("/jobs/{job_id}/logs")
@require_level(0)
async def get_job_logs(
    job_id: str,
    request: Request,
    lines: int = Query(100, ge=1, le=1000, description="日志行数"),
):
    """获取训练日志（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.get_job_logs(uuid.UUID(job_id), lines=lines)
    return {"code": "ok", "message": "获取成功", "data": result}


# --- 实例管理（P0） ---
@router.get("/jobs/{job_id}/instances")
@require_level(0)
async def list_instances(
    job_id: str,
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """训练实例列表（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.list_instances(
        job_id=uuid.UUID(job_id),
        page=page,
        page_size=page_size,
    )
    return {"code": "ok", "message": "获取成功", "data": result}


@router.post("/jobs/{job_id}/instances")
@require_level(0)
async def create_instance(job_id: str, req: CreateInstanceRequest, request: Request):
    """创建训练实例（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.create_instance(
        job_id=uuid.UUID(job_id),
        instance_name=req.instance_name,
        gpu_type=req.gpu_type,
    )
    return {"code": "ok", "message": "创建成功", "data": result}


@router.post("/instances/{instance_id}/start")
@require_level(0)
async def start_instance(instance_id: str, request: Request):
    """启动训练实例（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.start_instance(uuid.UUID(instance_id))
    return {"code": "ok", "message": "启动成功", "data": result}


@router.post("/instances/{instance_id}/stop")
@require_level(0)
async def stop_instance(instance_id: str, request: Request):
    """停止训练实例（P0）。"""
    container: ServiceContainer = request.app.state.container
    service = container.get("cloud_training")
    result = await service.stop_instance(uuid.UUID(instance_id))
    return {"code": "ok", "message": "停止成功", "data": result}
