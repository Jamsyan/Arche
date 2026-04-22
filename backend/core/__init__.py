"""Veil Core — Microkernel App Factory

Assembly order:
1. Load Config
2. Configure Logging
3. Initialize Database
4. Create ServiceContainer, register built-in services
5. Activate plugins (DAG-ordered setup)
6. Register plugin services into container
7. Setup middleware (CORS, error handlers)
8. Register startup/shutdown hooks
"""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import Config
from .container import ServiceContainer
from .db import init_db
from .middleware import register_error_handlers, setup_cors
from .plugin_registry import registry


def _setup_logging(config: Config) -> None:
    """Configure unified logging: console + optional file handler."""
    log_level = config.get("LOG_LEVEL", "INFO").upper()
    log_file = config.get("LOG_FILE")

    handlers = ["console"]
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(levelname)s:     %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": log_level,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
    }

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append("file")
        logging_config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": str(log_path),
            "level": log_level,
            "encoding": "utf-8",
        }
        logging_config["root"]["handlers"] = handlers

    logging.config.dictConfig(logging_config)


def create_app() -> FastAPI:
    # 1. Load config
    config = Config()

    # 2. Configure logging (before anything else runs)
    _setup_logging(config)

    # 3. Create container, register config
    container = ServiceContainer()

    # Sync to module-level singleton for plugins that import it directly
    from backend.core import container as _container_mod

    _container_mod.container = container

    container.register("config", lambda c: config)

    # 4. Init database (must be synchronous here — app factory cannot be async)
    database_url = config.get_required("DATABASE_URL")
    engine, session_factory = init_db(database_url)

    container.register(
        "db", lambda c: {"engine": engine, "session_factory": session_factory}
    )

    # 5. Create app
    app = FastAPI(title="Arche", version="0.1.0")

    # Store container on app for dependency injection
    app.state.container = container

    # 5. Activate plugins (DAG-ordered setup)
    registry.activate_all(app)

    # 6. Register plugin services into container
    registry.register_services(container)

    # 7. Middleware
    cors_origins = config.get("CORS_ORIGINS", "http://localhost:5173")
    setup_cors(app, [o.strip() for o in cors_origins.split(",")])
    register_error_handlers(app)

    # 8. Startup / Shutdown hooks
    @app.on_event("startup")
    async def startup():
        # 1. 先运行数据库迁移（alembic）
        import asyncio
        from alembic.config import Config as AlembicConfig
        from alembic import command
        from pathlib import Path

        migrations_dir = Path(__file__).resolve().parent.parent / "migrations"
        alembic_cfg = AlembicConfig()
        alembic_cfg.set_main_option("script_location", str(migrations_dir))
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: command.upgrade(alembic_cfg, "head"))

        # 2. 迁移完成后校验 schema 一致性（捕获漏掉的迁移）
        from .db import validate_schema

        await validate_schema()

        await registry.on_startup()

    @app.on_event("shutdown")
    async def shutdown():
        registry.on_shutdown()
        container.shutdown()

    # 9. Mount frontend static files (built Vue app)
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount(
            "/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend"
        )

    return app
