"""
Veil Core - Microkernel App Factory

The core is intentionally minimal. It provides only:
- Plugin registry
- Base FastAPI app wiring
- Static file serving
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .plugin_registry import registry


def create_app() -> FastAPI:
    """Application factory. Loads all active plugins and mounts them."""

    app = FastAPI(title="Veil", version="0.1.0")

    # Mount frontend static files (built Vue app)
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    # Activate all registered plugins
    registry.activate_all(app)

    return app
