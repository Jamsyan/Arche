"""爬虫插件 —— 流水线基础：CrawlItem 数据类 + BaseStage 抽象基类。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CrawlItem:
    """流水线中传递的数据项。"""

    url: str
    title: str = ""
    content: str = ""
    raw_html: str = ""
    links: list[str] = field(default_factory=list)
    status_code: int = 0
    headers: dict = field(default_factory=dict)
    content_type: str = ""  # article/post/nav/ad/functional/other
    source: str = ""
    user_agent: str = "Veil-Roamer/0.2.0"
    probe_result: dict = field(default_factory=dict)
    quality_passed: bool = True
    oss_path: str = ""
    file_size: int = 0
    error: str = ""


class BaseStage(ABC):
    """流水线车间基类。"""

    name: str = "base"

    @abstractmethod
    async def process(self, item: CrawlItem) -> CrawlItem | None:
        """处理数据项，返回 None 表示丢弃该任务。"""
        ...
