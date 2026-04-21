"""Crawler plugin — 数据模型。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.db import Base


class CrawlTask(Base):
    """爬虫任务表。"""

    __tablename__ = "crawl_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    seed_urls: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # JSON 数组字符串，如 ["https://example.com"]
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending"
    )  # pending / running / paused / completed / failed
    schedule_interval: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )  # 调度间隔（小时），0 表示仅执行一次
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CrawlResult(Base):
    """爬虫结果表。"""

    __tablename__ = "crawl_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    headers: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 字符串
    crawled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
