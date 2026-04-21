"""Blog plugin — 博客内容发布、浏览、互动插件。

负责帖子 CRUD、评论、点赞、审核、举报。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry

if TYPE_CHECKING:
    from fastapi import FastAPI
    from backend.core.container import ServiceContainer

# 导入模型，确保在 create_all 前注册到 Base
from backend.plugins.blog.models import BlogPost, BlogComment, BlogLike, BlogReport  # noqa: F401
from backend.plugins.blog.routes import router
from backend.plugins.blog.services import BlogService


class BlogPlugin(BasePlugin):
    name = "blog"
    version = "0.1.0"
    requires = []
    optional = ["auth"]

    def __init__(self):
        self._app = None

    def setup(self, app: "FastAPI") -> None:
        """注册路由。"""
        self._app = app
        app.include_router(router)

    def register_services(self, container: "ServiceContainer") -> None:
        """注册 BlogService 到容器。"""
        container.register("blog", lambda c: BlogService(c))

    def on_startup(self) -> None:
        pass

    def on_shutdown(self) -> None:
        pass


# 自注册
plugin = BlogPlugin()
registry.register("blog", plugin)
