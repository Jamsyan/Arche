"""资产管理插件 —— 资产聚合索引模型。

统一资产目录的索引表，用于跨插件资产搜索和统计。
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.db import Base


class AssetIndex(Base):
    """资产索引表：跨插件统一资产目录。"""

    __tablename__ = "asset_index"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    asset_type: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # file / blog_post / crawl_result / training_job
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_asset_index_owner_type", "owner_id", "asset_type"),
        Index("ix_asset_index_source", "asset_type", "source_id", unique=True),
    )
