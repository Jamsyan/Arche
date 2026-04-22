"""Crawler plugin — 存储车间：生成文件写入 OSS。"""

from __future__ import annotations

import gzip
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from backend.plugins.crawler.pipeline.base import BaseStage, CrawlItem

# 超过此大小的内容使用 gzip 压缩
_COMPRESS_THRESHOLD = 50_000

# 本地存储根目录（可通过环境变量覆盖）
_STORAGE_ROOT = Path(os.environ.get("CRAWLER_STORAGE_ROOT", "data/crawler"))


class StorageStage(BaseStage):
    """存储车间：一条任务产出一个文件（JSON 或 gzip），写入本地 OSS 目录。"""

    name = "storage"

    def __init__(self, container=None):
        self.container = container
        self._storage_root = _STORAGE_ROOT
        self._storage_root.mkdir(parents=True, exist_ok=True)

    async def process(self, item: CrawlItem) -> CrawlItem | None:
        if item.error or not item.quality_passed:
            return None

        # 生成文件内容
        record = {
            "url": item.url,
            "title": item.title,
            "content": item.content,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "source": item.source or urlparse(item.url).netloc,
            "user_agent": item.user_agent,
            "content_type": item.content_type,
            "status_code": item.status_code,
            "headers": dict(item.headers) if item.headers else {},
        }

        content_bytes = json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8")

        # 决定文件名和是否压缩
        ts = int(time.time() * 1000)
        domain = urlparse(item.url).netloc.replace(".", "_").replace(":", "_")
        if len(content_bytes) > _COMPRESS_THRESHOLD:
            filename = f"{domain}_{ts}.json.gz"
            content_bytes = gzip.compress(content_bytes)
        else:
            filename = f"{domain}_{ts}.json"

        # 按域名分目录
        dir_path = self._storage_root / domain.replace(".", "_").replace(":", "_")
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / filename

        # 写入文件
        file_path.write_bytes(content_bytes)

        item.oss_path = str(file_path.relative_to(self._storage_root))
        item.file_size = file_path.stat().st_size

        return item
