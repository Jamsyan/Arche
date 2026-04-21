"""Database layer — sync init (create_all), async sessions."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def init_db(database_url: str) -> tuple:
    # Sync engine for create_all (runs in this thread's context)
    sync_url = database_url.replace("+asyncpg", "")
    sync_engine = create_engine(sync_url, echo=False)
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    # Async engine for runtime use
    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)

    return engine, session_factory
