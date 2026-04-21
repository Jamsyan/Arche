"""Veil Core — Microkernel App Factory

Assembly order:
1. Load Config
2. Initialize Database
3. Create ServiceContainer, register built-in services
4. Activate plugins (DAG-ordered setup)
5. Register plugin services into container
6. Setup middleware (CORS, error handlers)
7. Register startup/shutdown hooks
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import Config
from .container import ServiceContainer
from .db import init_db, ensure_tables
from .middleware import register_error_handlers, setup_cors
from .plugin_registry import registry


def create_app() -> FastAPI:
    # 1. Load config
    config = Config()

    # 2. Create container, register config
    container = ServiceContainer()
    container.register("config", lambda c: config)

    # 3. Init database (must be synchronous here — app factory cannot be async)
    database_url = config.get_required("DATABASE_URL")
    engine, session_factory = init_db(database_url)

    container.register("db", lambda c: {"engine": engine, "session_factory": session_factory})

    # 4. Create app
    app = FastAPI(title="Veil", version="0.1.0")

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
        await ensure_tables(engine)
        registry.on_startup()

    @app.on_event("shutdown")
    async def shutdown():
        registry.on_shutdown()
        container.shutdown()

    # 9. Mount frontend static files (built Vue app)
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    return app
