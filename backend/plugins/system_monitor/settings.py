"""系统监控插件设置。"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class SystemMonitorSettings(BaseSettings):
    """系统监控配置。"""

    MONITOR_COLLECT_INTERVAL: int = Field(default=10, description="监控采集间隔 (秒)")

    class Config:
        extra = "allow"
