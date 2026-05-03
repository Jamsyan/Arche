"""爬虫插件 —— 流水线车间包入口。"""

from __future__ import annotations

from backend.plugins.crawler.pipeline.base import CrawlItem, BaseStage
from backend.plugins.crawler.pipeline.fetch import FetchStage
from backend.plugins.crawler.pipeline.parse import ParseStage
from backend.plugins.crawler.pipeline.classify import ClassifyStage
from backend.plugins.crawler.pipeline.quality import QualityStage
from backend.plugins.crawler.pipeline.storage import StorageStage

__all__ = [
    "CrawlItem",
    "BaseStage",
    "FetchStage",
    "ParseStage",
    "ClassifyStage",
    "QualityStage",
    "StorageStage",
]
