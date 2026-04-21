"""
Blog Plugin - Default plugin that serves as the public-facing blog.

This is the ONLY plugin active for anonymous/unauthenticated users.
It demonstrates the plugin pattern: self-contained routes + registration.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry


class BlogPlugin(BasePlugin):
    name = "blog"
    version = "0.1.0"

    def setup(self, app):
        router = APIRouter(prefix="/api/blog", tags=["blog"])

        @router.get("/posts")
        async def get_posts():
            """Return blog posts. Replace with real DB logic later."""
            return [
                {"id": 1, "title": "Hello Veil", "slug": "hello-veil", "excerpt": "First post on Veil."}
            ]

        app.include_router(router)


# Self-register
blog_plugin = BlogPlugin()
registry.register("blog", blog_plugin)
