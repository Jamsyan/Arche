"""搜索插件 —— API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Query, Request

from backend.core.container import ServiceContainer

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/suggestions")
async def search_suggestions(
    request: Request,
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(5, ge=1, le=20, description="最大返回条数"),
):
    """统一搜索建议。

    按 SID 前缀自动限定搜索范围：
      - user-* → 搜用户
      - asse-* → 搜资产（帖子、文件等）
      - task-* → 搜任务
      - log-*  → 搜日志
      - 无前缀 → 全局模糊搜索

    权限控制：
      - 公开信息无需登录可搜索
      - 敏感信息需要对应权限
    """
    container: ServiceContainer = request.app.state.container
    search_service = container.get("search")

    results = await search_service.search(
        keyword=q,
        limit=limit,
    )

    return {"code": "ok", "data": {"items": results}}
