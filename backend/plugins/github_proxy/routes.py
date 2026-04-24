"""GitHub 代理插件 —— 反向代理路由。

代理 GitHub API 和静态资源，支持缓存和 P1 权限控制。
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from backend.core.container import ServiceContainer
from backend.core.middleware import require_level

router = APIRouter(prefix="/api/github", tags=["github_proxy"])


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@require_level(1)
async def proxy_github(path: str, request: Request):
    """反向代理 GitHub API（需 P1 权限）。

    转发所有 HTTP 方法到 https://api.github.com/{path}，
    自动注入 GitHub Token，缓存 GET 请求。
    """
    from backend.core.middleware import require_user

    container: ServiceContainer = request.app.state.container
    proxy_service = container.get("github_proxy")
    user = require_user(request)

    query_params = dict(request.query_params)

    body = None
    if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()

    result = await proxy_service.proxy_request(
        method=request.method,
        path=path,
        query_params=query_params,
        headers=dict(request.headers),
        body=body,
        user_id=user["id"],
    )

    response_headers = {
        "X-GitHub-Cache": "HIT" if result["cached"] else "MISS",
    }

    status_code = result["status_code"]
    data = result["data"]

    return JSONResponse(
        status_code=status_code,
        content=data,
        headers=response_headers,
    )


@router.get("/raw/{path:path}")
@require_level(1)
async def proxy_raw(path: str, request: Request):
    """代理 GitHub 静态资源（需 P1 权限）。

    转发到 https://raw.githubusercontent.com/{path}，
    适用于 raw 文件内容（图片、文本等）。
    """
    container: ServiceContainer = request.app.state.container
    proxy_service = container.get("github_proxy")

    result = await proxy_service.proxy_raw_content(path=path)

    response_headers = {
        "X-GitHub-Cache": "HIT" if result["cached"] else "MISS",
    }

    content_type = result["headers"].get("Content-Type", "application/octet-stream")
    response_headers["Content-Type"] = content_type

    return Response(
        content=result["data"],
        status_code=result["status_code"],
        headers=response_headers,
    )


@router.post("/cache/clear")
@require_level(1)
async def clear_cache(request: Request):
    """清空代理缓存（需 P1 权限）。"""
    container: ServiceContainer = request.app.state.container
    proxy_service = container.get("github_proxy")
    count = proxy_service.clear_cache()
    return {
        "code": "ok",
        "message": f"已清空 {count} 条缓存",
        "data": {"cleared": count},
    }
