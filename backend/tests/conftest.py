"""pytest 配置和共享 fixture。"""

from __future__ import annotations

import sys
from pathlib import Path

# 把项目根目录加入 Python path (Arche/)，backend 的父目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from unittest.mock import MagicMock, AsyncMock


# =============================================================================
# 基础 Fixture
# =============================================================================


@pytest.fixture
def fake_container():
    """假的服务容器，模拟 config 返回测试值。"""
    container = MagicMock()

    class FakeConfig:
        _values = {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_CACHE_TTL": 300,
            "GITHUB_TIMEOUT": 10,
            "GITHUB_DEFAULT_MODE": "auto",
            "SECRET_KEY": "test_secret_key_12345",
        }

        def get_required(self, key):
            return self._values.get(key, "")

        def get(self, key, default=None):
            return self._values.get(key, default)

    container.get.return_value = FakeConfig()
    # Mock oss_rate_limiter，避免测试时需要真实的 RateLimiter
    mock_limiter = MagicMock()
    mock_limiter.consume = AsyncMock()
    container.get = lambda name: (
        FakeConfig() if name == "config" else mock_limiter
    )
    return container


@pytest.fixture
def anyio_backend():
    """asyncio 后端配置。"""
    return "asyncio"


# =============================================================================
# 数据库 Fixture
# =============================================================================


@pytest.fixture
async def in_memory_db():
    """内存 SQLite 数据库 fixture，自动建表，测试后清空。

    返回: {"engine": engine, "session_factory": session_factory}
    """
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from backend.core.db import Base

    # 创建内存数据库
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建 session factory
    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield {"engine": engine, "session_factory": session_factory}

    # 测试后关闭连接
    await engine.dispose()


@pytest.fixture
async def db_container(in_memory_db, fake_container):
    """带有真实内存数据库的 fake container。"""

    class FakeConfigWithDb:
        _values = {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_CACHE_TTL": 300,
            "GITHUB_TIMEOUT": 10,
            "GITHUB_DEFAULT_MODE": "auto",
            "SECRET_KEY": "test_secret_key_12345",
        }

        def get_required(self, key):
            return self._values.get(key, "")

        def get(self, key, default=None):
            return self._values.get(key, default)

    def get_service(name):
        if name == "db":
            return in_memory_db
        elif name == "config":
            return FakeConfigWithDb()
        elif name == "oss_rate_limiter":
            limiter = AsyncMock()
            limiter.consume = AsyncMock()
            return limiter
        # 对于 auth 等其他服务，返回一个 AsyncMock 容器
        service = AsyncMock()
        service.get.return_value = "mock"
        return service

    fake_container.get = get_service
    return fake_container


# =============================================================================
# Mock 辅助函数
# =============================================================================


def mock_subprocess_success(stdout: bytes = b'{"ok": true}', stderr: bytes = b""):
    """创建成功的 subprocess mock。"""

    class MockProc:
        returncode = 0

        async def communicate(self, input=None):
            return stdout, stderr

        async def wait(self):
            return 0

    return MockProc()


def mock_subprocess_failure(returncode: int = 1, stderr: bytes = b"error"):
    """创建失败的 subprocess mock。"""

    class MockProc:
        returncode = returncode

        async def communicate(self, input=None):
            return b"", stderr

    return MockProc()


# =============================================================================
# 集成测试 Fixture
# =============================================================================


@pytest.fixture
async def test_app(db_container):
    """创建真实的 FastAPI 测试应用，带内存数据库。"""
    from fastapi import FastAPI
    from backend.core.plugin_registry import registry, discover_plugins
    from backend.plugins.auth.middleware import AuthMiddleware

    # 先发现插件
    discover_plugins()

    # 创建测试 app，手动挂载路由
    app = FastAPI(title="Test Arche")
    app.state.container = db_container

    # 激活所有插件（注册路由）
    registry.activate_all(app)

    # 注册服务（挂载 AuthMiddleware 等）
    registry.register_services(db_container)

    # 手动挂载 AuthMiddleware（使用测试用的 SECRET_KEY）
    secret_key = db_container.get("config").get_required("SECRET_KEY")
    app.add_middleware(AuthMiddleware, secret_key=secret_key)

    yield app


@pytest.fixture
async def client(test_app):
    """HTTP 测试客户端。"""
    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_headers(db_container):
    """获取已认证用户的请求头。

    直接创建用户并生成 token，不走 HTTP 注册流程，更快更稳定。
    """
    from backend.plugins.auth.services import AuthService

    service = AuthService(db_container)

    # 先注册一个管理员（第一个用户）
    admin_result = await service.register(
        email="admin@example.com",
        username="admin",
        password="admin123"
    )

    # 再注册一个普通用户
    result = await service.register(
        email="test@example.com",
        username="testuser",
        password="testpass123"
    )

    return {"Authorization": f"Bearer {result['access_token']}"}


@pytest.fixture
async def admin_headers(db_container):
    """获取管理员的请求头。

    第一个注册的用户是 p0 (管理员)。
    """
    from backend.plugins.auth.services import AuthService

    service = AuthService(db_container)

    # 第一个注册的用户自动成为 p0
    result = await service.register(
        email="admin@example.com",
        username="admin",
        password="admin123"
    )

    return {"Authorization": f"Bearer {result['access_token']}"}
