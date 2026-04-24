"""BasePlugin —— 所有插件必须实现的抽象接口。"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI
    from .container import ServiceContainer


class BasePlugin(ABC):
    name: str = ""
    version: str = "0.1.0"
    requires: list[str] = []  # 硬依赖，没有就启动失败
    optional: list[str] = []  # 软依赖，没有就优雅降级

    @abstractmethod
    def setup(self, app: "FastAPI") -> None:
        """注册路由、中间件等。"""
        ...

    def register_services(self, container: "ServiceContainer") -> None:
        """可选：注册服务到容器。"""
        pass

    def on_startup(self) -> None:
        """可选：启动后钩子。"""
        pass

    def on_shutdown(self) -> None:
        """可选：关闭前钩子。"""
        pass
