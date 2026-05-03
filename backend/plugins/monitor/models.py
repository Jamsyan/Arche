"""监控插件 —— 监控大屏插件。

提供监控模板的 CRUD API。
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.db import Base


class MonitorTemplate(Base):
    """监控模板。"""

    __tablename__ = "monitor_templates"
    __allow_unmapped__ = True

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    components: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    refresh_interval: Mapped[int] = mapped_column(default=30)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "components": self.components or [],
            "refresh_interval": self.refresh_interval,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
