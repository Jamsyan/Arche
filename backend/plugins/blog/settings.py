"""博客插件设置。"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class BlogSettings(BaseSettings):
    """博客配置。"""

    SENSITIVE_WORDS: str = Field(default="", description="敏感词列表 (逗号分隔)")

    class Config:
        extra = "allow"
