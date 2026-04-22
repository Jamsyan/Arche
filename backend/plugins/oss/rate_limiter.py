"""Token Bucket 限速器 — 全局限速 + per-user 倍率微调。"""

from __future__ import annotations

import asyncio
import time
import uuid


class TokenBucket:
    """Token Bucket 算法：每秒补充 rate 个 token，容量为 capacity。"""

    def __init__(self, rate: float, capacity: float):
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
        self._last_refill = now

    async def consume(self, tokens: float) -> None:
        """消费指定数量的 token，不足则等待。"""
        while True:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return
            wait_time = (tokens - self._tokens) / max(self._rate, 1)
            await asyncio.sleep(wait_time)


class RateLimiterManager:
    """管理全局限速和 per-user 倍率。"""

    def __init__(self, global_rate: float = 10 * 1024 * 1024):
        """
        Args:
            global_rate: 全局限速，字节/秒，默认 10MB/s
        """
        self._global_bucket = TokenBucket(rate=global_rate, capacity=global_rate * 2)
        self._user_multipliers: dict[uuid.UUID, float] = {}

    async def consume(self, user_id: uuid.UUID | None, bytes_count: int) -> None:
        """按全局限速和 per-user 倍率进行消费。

        multiplier > 1 时等效加速（消耗更少 token），< 1 时降速。
        """
        multiplier = self._user_multipliers.get(user_id, 1.0) if user_id else 1.0
        effective_bytes = bytes_count / multiplier
        await self._global_bucket.consume(effective_bytes)

    def set_user_multiplier(self, user_id: uuid.UUID, multiplier: float) -> None:
        self._user_multipliers[user_id] = multiplier

    def remove_user_multiplier(self, user_id: uuid.UUID) -> None:
        self._user_multipliers.pop(user_id, None)

    def get_user_multiplier(self, user_id: uuid.UUID) -> float:
        return self._user_multipliers.get(user_id, 1.0)

    @property
    def global_rate(self) -> float:
        return self._global_bucket._rate

    def set_global_rate(self, rate: float) -> None:
        self._global_bucket._rate = rate
        self._global_bucket._capacity = rate * 2
