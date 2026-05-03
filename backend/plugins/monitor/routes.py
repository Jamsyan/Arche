"""监控插件路由 —— 监控模板 CRUD API。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from backend.plugins.monitor.models import MonitorTemplate

router = APIRouter(prefix="/api/monitor", tags=["monitor"])


def get_session_factory():
    """从容器获取 session factory。"""
    from backend.core.container import container as global_container

    db = global_container.get("db")
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db["session_factory"]


class TemplateCreate(BaseModel):
    name: str
    components: list[dict[str, Any]] = []
    refresh_interval: int = 30


class TemplateUpdate(BaseModel):
    name: str | None = None
    components: list[dict[str, Any]] | None = None
    refresh_interval: int | None = None


class ComponentDataResponse(BaseModel):
    id: str
    data: dict[str, Any]


@router.get("/templates")
async def list_templates() -> list[dict[str, Any]]:
    """获取用户的监控模板列表。"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(select(MonitorTemplate))
        templates = result.scalars().all()
        return [t.to_dict() for t in templates]


@router.post("/templates")
async def create_template(data: TemplateCreate) -> dict[str, Any]:
    """创建新的监控模板。"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        template = MonitorTemplate(
            name=data.name,
            components=data.components,
            refresh_interval=data.refresh_interval,
        )
        session.add(template)
        await session.commit()
        await session.refresh(template)
        return template.to_dict()


@router.get("/templates/{template_id}")
async def get_template(template_id: str) -> dict[str, Any]:
    """获取单个监控模板。"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(
            select(MonitorTemplate).where(MonitorTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template.to_dict()


@router.put("/templates/{template_id}")
async def update_template(template_id: str, data: TemplateUpdate) -> dict[str, Any]:
    """更新监控模板。"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(
            select(MonitorTemplate).where(MonitorTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        if data.name is not None:
            template.name = data.name
        if data.components is not None:
            template.components = data.components
        if data.refresh_interval is not None:
            template.refresh_interval = data.refresh_interval

        await session.commit()
        await session.refresh(template)
        return template.to_dict()


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str) -> dict[str, str]:
    """删除监控模板。"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(
            select(MonitorTemplate).where(MonitorTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        await session.delete(template)
        await session.commit()
        return {"message": "Template deleted"}


@router.get("/components/{component_id}/data")
async def get_component_data(component_id: str) -> dict[str, Any]:
    """获取组件数据。"""
    # TODO: 实现各组件的数据获取
    # 目前返回模拟数据
    return {
        "value": 0,
        "timestamp": None,
    }
