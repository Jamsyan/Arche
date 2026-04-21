"""Blog plugin — API routes."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from fastapi import APIRouter, Query, Request

from backend.core.container import ServiceContainer
from backend.core.middleware import require_level, require_user

router = APIRouter(prefix="/api/blog", tags=["blog"])


# --- 请求体模型 ---
class CreatePostRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256, description="标题")
    content: str = Field(..., min_length=1, description="正文内容")


class UpdatePostRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=256, description="标题")
    content: str | None = Field(None, min_length=1, description="正文内容")


class CreateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, description="评论内容")
    parent_id: str | None = Field(None, description="父评论 ID（回复）")


class CreateReportRequest(BaseModel):
    post_id: str = Field(..., description="被举报帖子 ID")
    reason: str | None = Field(None, max_length=500, description="举报原因")


# --- 公开路由：帖子列表/详情 ---
@router.get("/posts")
async def get_posts(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
):
    """帖子列表（公开，分页）。"""
    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.list_posts(
        page=page,
        page_size=page_size,
        status_filter="published",
        sort_by=sort_by,
    )
    return {"code": "ok", "message": "获取成功", "data": result}


@router.get("/posts/{slug}")
async def get_post(slug: str, request: Request):
    """帖子详情（公开）。"""
    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.get_post_by_slug(slug)
    return {"code": "ok", "message": "获取成功", "data": result}


# --- 需登录：发帖 ---
@router.post("/posts")
async def create_post(req: CreatePostRequest, request: Request):
    """发帖（需登录，进入审核队列）。"""
    user = require_user(request)
    author_id = uuid.UUID(user["id"])

    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.create_post(
        author_id=author_id,
        title=req.title,
        content=req.content,
    )
    return {"code": "ok", "message": "发帖成功，等待审核", "data": result}


# --- 作者本人：编辑 ---
@router.put("/posts/{post_id}")
async def update_post(post_id: str, req: UpdatePostRequest, request: Request):
    """编辑帖子（作者本人）。"""
    user = require_user(request)
    author_id = uuid.UUID(user["id"])

    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.update_post(
        post_id=uuid.UUID(post_id),
        author_id=author_id,
        title=req.title,
        content=req.content,
    )
    return {"code": "ok", "message": "编辑成功，重新进入审核", "data": result}


# --- 作者本人或 P0：删除 ---
@router.delete("/posts/{post_id}")
async def delete_post(post_id: str, request: Request):
    """删除帖子（作者本人 或 P0）。"""
    user = require_user(request)
    user_id = uuid.UUID(user["id"])
    user_level = user["level"]

    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    await blog_service.delete_post(
        post_id=uuid.UUID(post_id),
        user_id=user_id,
        user_level=user_level,
    )
    return {"code": "ok", "message": "删除成功", "data": {}}


# --- 公开：评论列表 ---
@router.get("/posts/{post_id}/comments")
async def get_comments(
    post_id: str,
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """评论列表（公开）。"""
    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.list_comments(
        post_id=uuid.UUID(post_id),
        page=page,
        page_size=page_size,
    )
    return {"code": "ok", "message": "获取成功", "data": result}


# --- 需登录：评论 ---
@router.post("/posts/{post_id}/comments")
async def create_comment(post_id: str, req: CreateCommentRequest, request: Request):
    """评论（需登录）。"""
    user = require_user(request)
    author_id = uuid.UUID(user["id"])

    parent_id = uuid.UUID(req.parent_id) if req.parent_id else None

    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.create_comment(
        post_id=uuid.UUID(post_id),
        author_id=author_id,
        content=req.content,
        parent_id=parent_id,
    )
    return {"code": "ok", "message": "评论成功", "data": result}


# --- 需登录：点赞（幂等） ---
@router.post("/posts/{post_id}/like")
async def toggle_like(post_id: str, request: Request):
    """点赞（需登录，幂等）。"""
    user = require_user(request)
    user_id = uuid.UUID(user["id"])

    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.toggle_like(
        post_id=uuid.UUID(post_id),
        user_id=user_id,
    )
    return {"code": "ok", "message": "操作成功", "data": result}


# --- P0：审核管理 ---
@router.get("/moderation/pending")
@require_level(0)
async def get_pending_posts(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """待审核列表（P0）。"""
    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.list_pending_posts(
        page=page,
        page_size=page_size,
    )
    return {"code": "ok", "message": "获取成功", "data": result}


@router.post("/moderation/{post_id}/approve")
@require_level(0)
async def approve_post(post_id: str, request: Request):
    """通过审核（P0）。"""
    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.approve_post(uuid.UUID(post_id))
    return {"code": "ok", "message": "审核通过", "data": result}


@router.post("/moderation/{post_id}/reject")
@require_level(0)
async def reject_post(post_id: str, request: Request):
    """拒绝审核（P0）。"""
    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.reject_post(uuid.UUID(post_id))
    return {"code": "ok", "message": "审核拒绝", "data": result}


# --- 需登录：举报 ---
@router.post("/reports")
async def create_report(req: CreateReportRequest, request: Request):
    """举报（需登录）。"""
    user = require_user(request)
    reporter_id = uuid.UUID(user["id"])

    container: ServiceContainer = request.app.state.container
    blog_service = container.get("blog")
    result = await blog_service.create_report(
        post_id=uuid.UUID(req.post_id),
        reporter_id=reporter_id,
        reason=req.reason,
    )
    return {"code": "ok", "message": "举报成功", "data": result}
