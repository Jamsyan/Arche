"""爬虫插件 —— 存储车间：通过 OSS 服务写入，统一元数据注册。"""

from __future__ import annotations

import gzip
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from backend.plugins.crawler.pipeline.base import BaseStage, CrawlItem

# 超过此大小的内容使用 gzip 压缩
_COMPRESS_THRESHOLD = 50_000


class StorageStage(BaseStage):
    """存储车间：通过 OSS 服务写入文件，自动注册到 oss_files 表。"""

    name = "storage"

    def __init__(self, container=None):
        self.container = container
        self._storage_service = None
        if container and container.is_available("storage"):
            self._storage_service = container.get("storage")

    async def process(self, item: CrawlItem) -> CrawlItem | None:
        if item.error or not item.quality_passed:
            return None

        ts = int(time.time() * 1000)
        domain = urlparse(item.url).netloc.replace(".", "_").replace(":", "_")

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
        if len(content_bytes) > _COMPRESS_THRESHOLD:
            filename = f"{domain}_{ts}.json.gz"
            content_bytes = gzip.compress(content_bytes)
        else:
            filename = f"{domain}_{ts}.json"

        mime_type = (
            "application/gzip" if filename.endswith(".gz") else "application/json"
        )

        # 通过 OSS 服务写入（注册到 oss_files 表，支持冷迁移）
        if self._storage_service:
            result = await self._storage_service.ingest_bytes(
                content=content_bytes,
                tenant_id="crawler",
                filename=filename,
                mime_type=mime_type,
                is_private=True,
            )
            item.oss_path = result["path"]
            item.file_size = result["size"]
        else:
            # 回退：直接写本地文件（无 oss_files 注册）
            storage_root = Path("data/crawler")
            dir_path = storage_root / domain
            dir_path.mkdir(parents=True, exist_ok=True)
            file_path = dir_path / filename
            file_path.write_bytes(content_bytes)
            item.oss_path = str(file_path.relative_to(storage_root))
            item.file_size = file_path.stat().st_size

        return item
