"""pytest 配置和共享 fixture。"""

from __future__ import annotations

import sys
from pathlib import Path

# 把项目根目录加入 Python path (Arche/)，backend 的父目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest  # noqa: E402
from unittest.mock import MagicMock, AsyncMock  # noqa: E402


# =============================================================================
# 自动 marker 分层
# =============================================================================
INTEGRATION_DIR = (Path(__file__).parent / "integration").resolve()


def pytest_collection_modifyitems(config, items):
    """自动给 backend/tests/integration/ 下的测试加 ``integration`` marker。

    这样：
    - 默认运行不变（仍然采集所有测试，整个套件保持稳定）；
    - 想跑纯单元测试时可以用 ``uv run pytest -m 'not integration'``
      获得快速反馈，CI 阶段也可以分层。
    """
    for item in items:
        try:
            test_path = Path(item.fspath).resolve()
        except (TypeError, ValueError):
            continue
        try:
            test_path.relative_to(INTEGRATION_DIR)
        except ValueError:
            continue
        item.add_marker(pytest.mark.integration)


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

    使用 StaticPool 让所有 session 共用同一个连接，避免
    `sqlite+aiosqlite:///:memory:` 默认每连接一份独立 DB 导致
    `Base.metadata.create_all` 建的表在后续 session 中"看不见"。
    """
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        async_sessionmaker,
    )
    from sqlalchemy.pool import StaticPool
    from backend.core.db import Base
    # 确保模型在 create_all 前已导入并注册到 Base.metadata
    from backend.core import models as _core_models  # noqa: F401
    from backend.plugins.asset_mgmt import models as _asset_models  # noqa: F401
    from backend.plugins.auth import models as _auth_models  # noqa: F401
    from backend.plugins.blog import models as _blog_models  # noqa: F401
    from backend.plugins.crawler import models as _crawler_models  # noqa: F401
    from backend.plugins.cloud_integration import models as _cloud_models  # noqa: F401
    from backend.plugins.monitor import models as _monitor_models  # noqa: F401
    from backend.plugins.oss import models as _oss_models  # noqa: F401

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    yield {"engine": engine, "session_factory": session_factory}

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

        def __init__(self):
            self._session_factory = in_memory_db["session_factory"]

        def get_required(self, key):
            return self._values.get(key, "")

        def get(self, key, default=None):
            return self._values.get(key, default)

        def invalidate_cache(self, key=None):
            return None

    def get_service(name):
        if name == "db":
            return in_memory_db
        elif name == "config":
            return FakeConfigWithDb()
        elif name == "auth":
            from backend.plugins.auth.services import AuthService

            return AuthService(fake_container)
        elif name == "github":
            from backend.plugins.github_proxy.services import GitHubService

            return GitHubService(fake_container)
        elif name == "storage":
            from backend.plugins.oss.services import StorageService

            return StorageService(fake_container)
        elif name == "asset_mgmt":
            from backend.plugins.asset_mgmt.services import AssetMgmtService

            return AssetMgmtService(fake_container)
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


def patch_container_service(container, name: str, service):
    """把 ``container.get(name)`` 临时替换成 ``service``，其它名字透传旧 get。

    用于 ``db_container`` 这种共享 fixture 中按需注入特定 mock service，
    替代各测试反复写：
    ::

        old_get = db_container.get
        def _get(n): return service if n == name else old_get(n)
        db_container.get = _get

    Returns:
        传入的 ``service``，方便链式赋值给 fixture 返回值。
    """
    old_get = container.get

    def _get(n: str):
        if n == name:
            return service
        return old_get(n)

    container.get = _get
    return service


# =============================================================================
# 集成测试 Fixture
# =============================================================================


@pytest.fixture
async def test_app(db_container):
    """创建真实的 FastAPI 测试应用，带内存数据库。

    与生产 `create_app` 的关键差异说明：
    - 这里手动挂载 plugin 路由 + AuthMiddleware；
    - 同时调用 `register_error_handlers`，让 `AppError`/`AuthError`/
      `PermissionError` 能正确映射成 4xx 响应，而不是被 starlette
      默认 500 吃掉，否则集成测试只能看到 500 而无法断言业务码。
    """
    from fastapi import FastAPI
    from backend.core.plugin_registry import registry, discover_plugins
    from backend.core.middleware import register_error_handlers
    from backend.plugins.auth.middleware import AuthMiddleware

    discover_plugins()

    app = FastAPI(title="Test Arche")
    app.state.container = db_container

    register_error_handlers(app)

    registry.activate_all(app)
    registry.register_services(db_container)

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
    await service.register(
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


# =============================================================================
# Crawler Fixture
# =============================================================================


@pytest.fixture
def crawler_sample_url():
    return "https://example.com/article/hello"


@pytest.fixture
def crawler_sample_html():
    return """
    <html>
      <head>
        <title>Test Article</title>
      </head>
      <body>
        <main>
          <p>This is crawler sample content with enough characters for quality checks.</p>
          <a href="/next">Next</a>
          <a href="https://example.com/about">About</a>
        </main>
      </body>
    </html>
    """


@pytest.fixture
def crawler_item_factory():
    from backend.plugins.crawler.pipeline import CrawlItem

    def _create(**kwargs):
        defaults = {
            "url": "https://example.com/article/hello",
            "source": "example.com",
            "status_code": 200,
            "quality_passed": True,
            "headers": {"content-type": "text/html"},
        }
        defaults.update(kwargs)
        return CrawlItem(**defaults)

    return _create


# =============================================================================
# Monitor Fixture
# =============================================================================


@pytest.fixture
def monitor_template_payload():
    return {
        "name": "CPU Dashboard",
        "components": [{"id": "cpu", "type": "metric"}],
        "refresh_interval": 15,
    }
