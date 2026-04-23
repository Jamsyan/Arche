"""Database layer — async engine + lazy create_all."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# 模块级变量，供 on_startup 等场景使用
engine: Optional[AsyncEngine] = None
session_factory: Optional[async_sessionmaker[AsyncSession]] = None
_initialized = False


async def ensure_tables() -> None:
    """Lazy create tables on first async context (avoids event loop conflicts)."""
    global _initialized
    if _initialized:
        return
    assert engine is not None, "Database not initialized. Call init_db() first."
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _initialized = True


def init_db(database_url: str) -> tuple:
    global engine, session_factory
    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)
    return engine, session_factory


async def validate_schema() -> None:
    """启动时校验数据库 schema 是否与模型一致。"""
    assert engine is not None, "Database not initialized. Call init_db() first."
    async with engine.begin() as conn:
        result = await conn.run_sync(_validate_schema_sync)
        if result:
            raise RuntimeError(
                f"数据库 schema 与模型不一致，请执行 migration 修复：\n{result}"
            )


def _validate_schema_sync(conn):
    """同步检查所有表的列是否匹配模型定义。"""
    from sqlalchemy import text as sa_text

    issues = []
    # 检测数据库类型
    is_postgresql = conn.dialect.name == "postgresql"

    for table_name, table in Base.metadata.tables.items():
        try:
            if is_postgresql:
                result = conn.execute(
                    sa_text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = :table"
                    ),
                    {"table": table_name},
                )
                db_cols = {row[0] for row in result.fetchall()}
            else:
                result = conn.execute(sa_text(f"PRAGMA table_info({table_name})"))
                db_cols = {row[1] for row in result.fetchall()}
        except Exception:
            continue  # 表不存在，会在后续 create_all/migration 中创建

        model_cols = set(table.c.keys())
        missing = model_cols - db_cols
        if missing:
            issues.append(f"  {table_name} 缺少列: {', '.join(sorted(missing))}")

    return "\n".join(issues) if issues else ""
