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


_DEFAULT_CONFIG_SEED = [
    # (key, group, description, is_sensitive)
    ("MINIO_ENDPOINT", "minio", "MinIO 服务地址", False),
    ("MINIO_ROOT_USER", "minio", "MinIO 管理员用户名", False),
    ("MINIO_ROOT_PASSWORD", "minio", "MinIO 管理员密码", True),
    ("MINIO_SECURE", "minio", "是否启用 TLS", False),
    ("OSS_ACCESS_KEY_ID", "oss", "阿里云 OSS AccessKey ID", True),
    ("OSS_ACCESS_KEY_SECRET", "oss", "阿里云 OSS AccessKey Secret", True),
    ("OSS_ENDPOINT", "oss", "阿里云 OSS Endpoint", False),
    ("OSS_BUCKET_NAME", "oss", "阿里云 OSS Bucket 名称", False),
    ("CLOUD_PROVIDER", "cloud", "云训练 Provider (mock/zhixingyun/aliyun)", False),
    ("ZHIXINGYUN_API_KEY", "cloud", "智星云 API Key", True),
    ("ZHIXINGYUN_API_SECRET", "cloud", "智星云 API Secret", True),
    ("ALIYUN_ACCESS_KEY_ID", "cloud", "阿里云 ECS AccessKey ID", True),
    ("ALIYUN_ACCESS_KEY_SECRET", "cloud", "阿里云 ECS AccessKey Secret", True),
    ("ALIYUN_REGION", "cloud", "阿里云 ECS Region", False),
    ("ALIYUN_SECURITY_GROUP_ID", "cloud", "阿里云安全组 ID", False),
    ("ALIYUN_VSWITCH_ID", "cloud", "阿里云交换机 ID", False),
    ("ALIYUN_IMAGE_ID", "cloud", "阿里云镜像 ID", False),
    ("CLOUD_API_KEY", "cloud", "通用云 API Key", True),
    ("CLOUD_API_SECRET", "cloud", "通用云 API Secret", True),
    ("GITHUB_TOKEN", "github", "GitHub API Token", True),
    ("GITHUB_API_BASE", "github", "GitHub API Base URL", False),
    ("GITHUB_RAW_BASE", "github", "GitHub Raw Base URL", False),
    ("GITHUB_CACHE_TTL", "github", "GitHub 缓存 TTL (秒)", False),
    ("GITHUB_TIMEOUT", "github", "GitHub 请求超时 (秒)", False),
    ("CRAWLER_SEEDS", "crawler", "爬虫种子 URL", False),
    ("CRAWLER_STORAGE_ROOT", "crawler", "爬虫存储目录", False),
    ("LOG_LEVEL", "logging", "日志级别 (DEBUG/INFO/WARNING/ERROR)", False),
    ("LOG_FILE", "logging", "日志文件路径", False),
    ("MONITOR_COLLECT_INTERVAL", "system", "监控采集间隔 (秒)", False),
    ("SENSITIVE_WORDS", "system", "敏感词列表 (逗号分隔)", False),
    ("DEPLOY_TOKEN", "deploy", "部署 Webhook Token", True),
]


async def _seed_default_config(config: Config, session_factory) -> None:
    """将 .env 中的默认值初始化到数据库（仅首次启动时）。"""
    try:
        from sqlalchemy import select

        from backend.core.models import ConfigEntry

        async with session_factory() as session:
            # 检查表是否已有数据
            result = await session.execute(select(ConfigEntry).limit(1))
            if result.first():
                return  # 已有数据，跳过 seed

            for key, group, desc, sensitive in _DEFAULT_CONFIG_SEED:
                value = config.get(key, "")
                if not value and key == "LOG_LEVEL":
                    value = "INFO"  # 兜底默认值

                entry = ConfigEntry(
                    key=key,
                    group=group,
                    description=desc,
                    is_sensitive=sensitive,
                    value=value,
                )
                session.add(entry)

            await session.commit()
    except Exception as e:
        logging.warning(f"Config seed skipped: {e}")


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

        # 3. 注入 session_factory 到 config，启用 DB 配置回退
        config.set_session_factory(session_factory)

        # 4. 初始化种子配置（仅首次启动时）
        await _seed_default_config(config, session_factory)

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
