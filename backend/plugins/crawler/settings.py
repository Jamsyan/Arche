"""爬虫插件设置。"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class CrawlerSettings(BaseSettings):
    """爬虫配置。"""

    CRAWLER_SEEDS: str = Field(default="", description="爬虫种子 URL (逗号分隔)")
    CRAWLER_STORAGE_ROOT: str = Field(default="", description="爬虫存储目录")

    class Config:
        extra = "allow"
