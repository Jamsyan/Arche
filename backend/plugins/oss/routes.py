"""OSS plugin — 路由：上传/下载/删除/列表/外部写入/存储统计/配额管理。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request, UploadFile, File, Form, Query

from backend.core.container import ServiceContainer
from backend.core.middleware import require_user, require_level


router = APIRouter(prefix="/api/oss", tags=["oss"])


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    is_private: bool = Form(default=False),
):
    """用户上传文件。"""
    user = require_user(request)
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    result = await storage_service.upload_file(
        file=file,
        owner_id=uuid.UUID(user["id"]),
        user_level=user["level"],
        is_private=is_private,
    )
    return {"code": "ok", "message": "上传成功", "data": result}


@router.get("/files/{file_id}")
async def download_file(file_id: str, request: Request):
    """下载文件，返回文件元数据。"""
    user = require_user(request)
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    file_path, meta = await storage_service.download_file(
        file_id=uuid.UUID(file_id),
        requester_id=uuid.UUID(user["id"]),
        requester_level=user["level"],
    )
    from fastapi.responses import FileResponse

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type=meta.get("mime_type", "application/octet-stream"),
    )


@router.delete("/files/{file_id}")
async def delete_file(file_id: str, request: Request):
    """删除文件。"""
    user = require_user(request)
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    await storage_service.delete_file(
        file_id=uuid.UUID(file_id),
        requester_id=uuid.UUID(user["id"]),
        requester_level=user["level"],
    )
    return {"code": "ok", "message": "删除成功", "data": {}}


@router.get("/my")
async def list_my_files(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """我的文件列表。"""
    user = require_user(request)
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    files = await storage_service.list_my_files(
        user_id=uuid.UUID(user["id"]),
        limit=limit,
        offset=offset,
    )
    return {"code": "ok", "message": "获取成功", "data": {"files": files}}


@router.post("/external/{tenant_id}/upload")
async def external_upload(
    tenant_id: str,
    request: Request,
    file: UploadFile = File(...),
):
    """外部租户写入文件。"""
    # 外部接口也需要认证（后续可改为租户 API Key 鉴权）
    require_user(request)
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    result = await storage_service.external_upload(
        file=file,
        tenant_id=tenant_id,
    )
    return {"code": "ok", "message": "上传成功", "data": result}


@router.get("/external/{tenant_id}/files")
async def list_external_files(
    tenant_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """外部租户文件列表。"""
    require_user(request)
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    files = await storage_service.list_external_files(
        tenant_id=tenant_id,
        limit=limit,
        offset=offset,
    )
    return {"code": "ok", "message": "获取成功", "data": {"files": files}}


@router.get("/storage/stats")
async def get_storage_stats(
    request: Request,
    user_scope: bool = Query(default=False),
):
    """存储统计。默认全局统计，user_scope=true 时仅统计当前用户。"""
    user = require_user(request)
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    user_id = uuid.UUID(user["id"]) if user_scope else None
    stats = await storage_service.get_storage_stats(user_id=user_id)
    return {"code": "ok", "message": "获取成功", "data": stats}


@router.get("/quota")
async def get_quota(request: Request):
    """P1 用户存储配额使用情况。"""
    user = require_user(request)
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    quota = await storage_service.get_p1_quota_used(uuid.UUID(user["id"]))
    return {"code": "ok", "message": "获取成功", "data": quota}


@router.post("/admin/evict")
@require_level(0)
async def trigger_eviction(
    request: Request,
    days: int = Query(default=7, ge=1, le=30),
):
    """手动触发冷热迁移（P0）。"""
    container: ServiceContainer = request.app.state.container
    storage_service = container.get("storage")
    count = await storage_service.evict_cold_files(days=days)
    return {"code": "ok", "message": f"迁移完成，{count} 个文件已推到阿里云", "data": {"migrated": count}}
