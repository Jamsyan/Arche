"""Core application settings."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """核心应用配置。"""

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/arche.db",
        description="数据库连接字符串",
    )

    SECRET_KEY: str = Field(
        default="change-me-to-random-string",
        description="JWT 签名密钥，生产环境必须更换",
    )

    CORS_ORIGINS: str = Field(
        default="http://localhost:5173",
        description="跨域来源，多个用逗号分隔",
    )

    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str | None = Field(default=None, description="日志文件路径")

    class Config:
        env_prefix = ""
        extra = "allow"
