"""Core domain models — cross-cutting concern models that don't belong to any plugin."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.db import Base


class ConfigEntry(Base):
    """运行时配置条目，替代 .env 中的业务配置。"""

    __tablename__ = "config_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    group: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, server_default="general"
    )
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
