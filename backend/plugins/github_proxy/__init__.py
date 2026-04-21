"""GitHub Proxy plugin — GitHub API 反向代理插件。

负责代理 GitHub API 和静态资源，支持缓存和 Token 注入。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.base_plugin import BasePlugin
from backend.core.plugin_registry import registry

if TYPE_CHECKING:
    from fastapi import FastAPI
    from backend.core.container import ServiceContainer

from backend.plugins.github_proxy.routes import router
from backend.plugins.github_proxy.services import GitHubProxyService


class GithubProxyPlugin(BasePlugin):
    name = "github_proxy"
    version = "0.1.0"
    requires = ["auth"]
    optional = []

    def __init__(self):
        self._app = None

    def setup(self, app: "FastAPI") -> None:
        """注册路由。"""
        self._app = app
        app.include_router(router)

    def register_services(self, container: "ServiceContainer") -> None:
        """注册 GitHubProxyService 到容器。"""
        container.register("github_proxy", lambda c: GitHubProxyService(c))

    def on_startup(self) -> None:
        pass

    def on_shutdown(self) -> None:
        pass


# 自注册
plugin = GithubProxyPlugin()
registry.register("github_proxy", plugin)
