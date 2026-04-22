"""Crawler plugin — URL 调度器：待爬队列 + 按域名限流。"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from urllib.parse import urlparse


class UrlScheduler:
    """URL 调度器：管理待爬队列，按域名限制并发。"""

    def __init__(self, max_global: int = 5, max_per_domain: int = 2):
        self._max_global = max_global
        self._max_per_domain = max_per_domain
        self._queue: list[str] = []
        self._queue_lock = asyncio.Lock()
        self._global_semaphore = asyncio.Semaphore(max_global)
        self._domain_slots: dict[str, asyncio.Semaphore] = {}
        self._domain_slots_lock = asyncio.Lock()
        self._domain_active: dict[str, int] = defaultdict(int)
        self._active_count = 0

    async def enqueue(self, url: str) -> None:
        """将 URL 加入待爬队列。"""
        async with self._queue_lock:
            self._queue.append(url)

    async def dequeue(self) -> str | None:
        """从队列取出一个 URL（受域名限流约束）。"""
        async with self._queue_lock:
            if not self._queue:
                return None
            # 找一个域名未超限的 URL
            for i, url in enumerate(self._queue):
                domain = self._get_domain(url)
                if self._domain_active.get(domain, 0) < self._max_per_domain:
                    self._queue.pop(i)
                    return url
            return None

    async def can_fetch(self, url: str) -> bool:
        """检查该域名是否还有并发配额。"""
        domain = self._get_domain(url)
        return self._domain_active.get(domain, 0) < self._max_per_domain

    async def acquire(self, url: str) -> None:
        """获取抓取权限（全局 + 域名信号量）。"""
        domain = self._get_domain(url)
        await self._global_semaphore.acquire()
        domain_sem = await self._get_domain_semaphore(domain)
        await domain_sem.acquire()
        self._domain_active[domain] += 1
        self._active_count += 1

    async def release(self, url: str) -> None:
        """释放抓取权限。"""
        domain = self._get_domain(url)
        self._global_semaphore.release()
        if domain in self._domain_slots:
            self._domain_slots[domain].release()
        self._domain_active[domain] = max(0, self._domain_active.get(domain, 0) - 1)
        self._active_count = max(0, self._active_count - 1)

    async def _get_domain_semaphore(self, domain: str) -> asyncio.Semaphore:
        """获取或创建域名的并发限制信号量。"""
        async with self._domain_slots_lock:
            if domain not in self._domain_slots:
                self._domain_slots[domain] = asyncio.Semaphore(self._max_per_domain)
            return self._domain_slots[domain]

    @property
    def active_count(self) -> int:
        return self._active_count

    @property
    def queue_size(self) -> int:
        return len(self._queue)

    @property
    def domains_active(self) -> dict[str, int]:
        return dict(self._domain_active)

    @staticmethod
    def _get_domain(url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return url
