from __future__ import annotations

import pytest


XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert(1)",
    '"><script>alert(1)</script>',
]

SQLI_PAYLOADS = [
    "' OR 1=1 --",
    "' UNION SELECT * FROM users --",
    "1; DROP TABLE posts; --",
    "admin'--",
    "' OR '1'='1",
]

PATH_TRAVERSAL_PAYLOADS = [
    "../../../etc/passwd",
    "..\\..\\..\\system32\\config",
    "....//....//etc/shadow",
    "../../evil.png",
]

JWT_ALG_NONE_PAYLOAD = (
    "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0"
    ".eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDIiLCJsZXZlbCI6MCwiZXhwIjo5OTk5OTk5OTk5fQ"
    "."
)

JWT_WRONG_SECRET = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDIiLCJsZXZlbCI6MCwiZXhwIjo5OTk5OTk5OTk5fQ"
    ".dGhpcyBpcyBhIHdyb25nIHNpZ25hdHVyZQ"
)


# Workaround for plugin_registry module caching bug:
# registry.reset() + discover_plugins() fails on subsequent calls because
# importlib caches already-imported modules, preventing __init__.py from
# re-registering plugins. We build the test app manually instead.


@pytest.fixture
async def adversarial_app(db_container):
    from fastapi import FastAPI
    from backend.core.middleware import register_error_handlers
    from backend.plugins.auth.middleware import AuthMiddleware

    app = FastAPI(title="Test Arche")
    app.state.container = db_container

    register_error_handlers(app)

    from backend.plugins.auth.routes import router as auth_router
    from backend.plugins.blog.routes import router as blog_router
    from backend.plugins.oss.routes import router as oss_router
    from backend.plugins.search.routes import router as search_router
    from backend.plugins.config_mgmt.routes import router as config_router
    from backend.plugins.crawler.routes import router as crawler_router

    app.include_router(auth_router)
    app.include_router(blog_router)
    app.include_router(oss_router)
    app.include_router(search_router)
    app.include_router(config_router)
    app.include_router(crawler_router)

    secret_key = db_container.get("config").get_required("SECRET_KEY")
    app.add_middleware(AuthMiddleware, secret_key=secret_key)

    yield app


@pytest.fixture
async def client(adversarial_app):
    from httpx import AsyncClient, ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=adversarial_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def unique_email():
    import uuid

    return f"user_{uuid.uuid4().hex[:8]}@example.com"
