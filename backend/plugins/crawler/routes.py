"""Crawler plugin — API 路由：任务管理、结果查询、执行抓取。"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from fastapi import APIRouter, Query, Request

from backend.core.container import ServiceContainer
from backend.core.middleware import require_level


router = APIRouter(prefix="/api/crawler", tags=["crawler"])


# --- 请求体模型 ---
class CreateTaskRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=256, description="任务名称")
    seed_urls: list[str] = Field(
        ..., min_length=1, max_length=100, description="种子 URL 列表"
    )
    schedule_interval: int = Field(
        default=0, ge=0, le=168, description="调度间隔（小时），0 表示仅执行一次"
    )
    max_depth: int = Field(
        default=1, ge=0, le=5, description="链接扩展深度（0 = 不扩展）"
    )
    max_pages: int = Field(
        default=100, ge=1, le=10000, description="最大抓取页数"
    )
    concurrency: int = Field(
        default=3, ge=1, le=10, description="并发数"
    )
    request_delay: float = Field(
        default=1.0, ge=0.1, le=60, description="同站请求间隔秒数"
    )


# --- 任务管理（全部 P0） ---


@router.post("/tasks")
@require_level(0)
async def create_task(req: CreateTaskRequest, request: Request):
    """创建爬虫任务（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    result = await crawler_service.create_task(
        name=req.name,
        seed_urls=req.seed_urls,
        schedule_interval=req.schedule_interval,
    )
    # 更新扩展字段（create_task 不接收这些字段，直接更新数据库）
    from sqlalchemy import update as sql_update
    from backend.plugins.crawler.models import CrawlTask

    task_id = result["id"]
    async with crawler_service.session_factory() as session:
        await session.execute(
            sql_update(CrawlTask)
            .where(CrawlTask.id == uuid.UUID(task_id))
            .values(
                max_depth=req.max_depth,
                max_pages=req.max_pages,
                concurrency=req.concurrency,
                request_delay=int(req.request_delay * 100),  # 存储为整数
                respect_robots=1,
            )
        )
        await session.commit()

    return {"code": "ok", "message": "创建成功", "data": result}


@router.get("/tasks")
@require_level(0)
async def list_tasks(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: str | None = Query(None, description="按状态筛选"),
):
    """任务列表（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    result = await crawler_service.list_tasks(
        page=page,
        page_size=page_size,
        status_filter=status,
    )
    return {"code": "ok", "message": "获取成功", "data": result}


@router.get("/tasks/{task_id}")
@require_level(0)
async def get_task(task_id: str, request: Request):
    """任务详情（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    result = await crawler_service.get_task(uuid.UUID(task_id))
    return {"code": "ok", "message": "获取成功", "data": result}


@router.post("/tasks/{task_id}/run")
@require_level(0)
async def run_task(task_id: str, request: Request):
    """执行爬虫任务（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    results = await crawler_service.execute_task(uuid.UUID(task_id))
    return {"code": "ok", "message": "执行完成", "data": {"results": results}}


@router.post("/tasks/{task_id}/pause")
@require_level(0)
async def pause_task(task_id: str, request: Request):
    """暂停爬虫任务（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    result = await crawler_service.update_task_status(
        uuid.UUID(task_id), "paused"
    )
    return {"code": "ok", "message": "已暂停", "data": result}


@router.post("/tasks/{task_id}/resume")
@require_level(0)
async def resume_task(task_id: str, request: Request):
    """恢复爬虫任务（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    result = await crawler_service.update_task_status(
        uuid.UUID(task_id), "pending"
    )
    return {"code": "ok", "message": "已恢复", "data": result}


@router.delete("/tasks/{task_id}")
@require_level(0)
async def delete_task(task_id: str, request: Request):
    """删除爬虫任务（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    await crawler_service.delete_task(uuid.UUID(task_id))
    return {"code": "ok", "message": "删除成功", "data": {}}


# --- 结果管理（全部 P0） ---


@router.get("/tasks/{task_id}/results")
@require_level(0)
async def list_results(
    task_id: str,
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """任务结果列表（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    result = await crawler_service.list_results(
        task_id=uuid.UUID(task_id),
        page=page,
        page_size=page_size,
    )
    return {"code": "ok", "message": "获取成功", "data": result}


@router.get("/results/{result_id}")
@require_level(0)
async def get_result(result_id: str, request: Request):
    """结果详情（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    result = await crawler_service.get_result(uuid.UUID(result_id))
    return {"code": "ok", "message": "获取成功", "data": result}


# --- 统计 ---


@router.get("/stats")
@require_level(0)
async def get_stats(request: Request):
    """爬虫统计（P0）。"""
    container: ServiceContainer = request.app.state.container
    crawler_service = container.get("crawler")
    result = await crawler_service.get_stats()
    return {"code": "ok", "message": "获取成功", "data": result}
