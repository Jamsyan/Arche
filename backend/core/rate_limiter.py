"""内存速率限制器 —— 用于登录等敏感端点的暴力破解防护。

使用滑动窗口计数，基于 identity + IP 进行限流。
单机内存实现，多实例部署需要 Redis 共享状态。
"""

from __future__ import annotations

import time
from collections import defaultdict


class RateLimiter:
    """滑动窗口速率限制器。

    用法:
        limiter = RateLimiter(max_attempts=5, window_seconds=60)
        if limiter.is_limited("admin-127.0.0.1"):
            raise AppError("尝试次数过多，请 60 秒后再试")
    """

    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        # {key: [timestamp, ...]}
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def is_limited(self, key: str) -> bool:
        """检查该 key 是否已被限流。"""
        now = time.time()
        window_start = now - self.window_seconds
        # 清理窗口外的旧记录
        self._attempts[key] = [t for t in self._attempts[key] if t > window_start]
        return len(self._attempts[key]) >= self.max_attempts

    def record_attempt(self, key: str) -> int:
        """记录一次尝试，返回当前窗口内的尝试次数。"""
        now = time.time()
        window_start = now - self.window_seconds
        self._attempts[key] = [t for t in self._attempts[key] if t > window_start]
        self._attempts[key].append(now)
        return len(self._attempts[key])

    def reset(self, key: str) -> None:
        """重置某个 key 的计数（登录成功后调用）。"""
        self._attempts.pop(key, None)
