"""Configuration management — env file + env vars + DB fallback + cache."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any


class Config:
    """Layered config: defaults < .env < environment variables < DB (cached)."""

    def __init__(self, env_file: str = ".env"):
        self._values: dict[str, str] = {}
        self._load_env_file(env_file)
        self._load_os_environ()

        # DB-backed cache layer
        self._cache: dict[str, tuple[str, float]] = {}  # key -> (value, expiry_ts)
        self._cache_ttl: int = 60
        self._session_factory: Any = None  # set during startup

    def _load_env_file(self, env_file: str) -> None:
        path = Path(env_file)
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            self._values[key.strip()] = value.strip().strip("\"'")

    def _load_os_environ(self) -> None:
        for key, value in os.environ.items():
            if (
                key in self._values
                or key.startswith("VEIL_")
                or key
                in (
                    "DATABASE_URL",
                    "SECRET_KEY",
                    "CORS_ORIGINS",
                )
            ):
                self._values[key] = value

    def get(self, key: str, default: str | None = None) -> str | None:
        # Layer 1: .env / OS env (highest priority for startup-critical keys)
        if key in self._values:
            return self._values[key]

        # Layer 2: in-memory cache
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                del self._cache[key]

        # Layer 3: DB fallback
        if self._session_factory:
            db_value = self._fetch_from_db(key)
            if db_value is not None:
                self._cache[key] = (db_value, time.time() + self._cache_ttl)
                return db_value

        return default

    def _fetch_from_db(self, key: str) -> str | None:
        """Query ConfigEntry from database. Returns None on any error."""
        try:
            import asyncio

            from backend.core.models import ConfigEntry

            async def _query():
                async with self._session_factory() as session:
                    from sqlalchemy import select

                    result = await session.execute(
                        select(ConfigEntry).where(ConfigEntry.key == key)
                    )
                    entry = result.scalar_one_or_none()
                    return entry.value if entry else None

            # If we're in an async context we can't block — use threading
            # But config.get() is called from sync code, so we need a new event loop
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _query())
                return future.result(timeout=5)
        except Exception:
            return None

    def get_required(self, key: str) -> str:
        value = self.get(key)
        if value is None:
            raise RuntimeError(f"Required config '{key}' is not set")
        return value

    def set(self, key: str, value: str) -> None:
        self._values[key] = value

    def invalidate_cache(self, key: str | None = None) -> None:
        """Clear cache entry (single key or all)."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    def set_session_factory(self, session_factory: Any) -> None:
        """Attach DB session factory after app startup."""
        self._session_factory = session_factory

    def set_cache_ttl(self, seconds: int) -> None:
        self._cache_ttl = seconds
