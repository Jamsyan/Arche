"""GitHub 代理插件设置。"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class GitHubProxySettings(BaseSettings):
    """GitHub 代理配置。"""

    GITHUB_TOKEN: str = Field(default="", description="GitHub API Token")
    GITHUB_API_BASE: str = Field(
        default="https://api.github.com", description="GitHub API Base URL"
    )
    GITHUB_RAW_BASE: str = Field(
        default="https://raw.githubusercontent.com", description="GitHub Raw Base URL"
    )
    GITHUB_CACHE_TTL: int = Field(default=300, description="缓存 TTL (秒)")
    GITHUB_TIMEOUT: int = Field(default=30, description="请求超时 (秒)")

    class Config:
        extra = "allow"
