"""Database layer — async engine + lazy create_all."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_initialized = False


async def ensure_tables(engine) -> None:
    """Lazy create tables on first async context (avoids event loop conflicts)."""
    global _initialized
    if _initialized:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _initialized = True


def init_db(database_url: str) -> tuple:
    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)
    return engine, session_factory
