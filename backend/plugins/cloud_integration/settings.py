"""Cloud integration plugin settings."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class CloudIntegrationSettings(BaseSettings):
    """云集成配置。"""

    CLOUD_PROVIDER: str = Field(default="mock", description="云 Provider (mock/zhixingyun/aliyun)")

    # 智星云
    ZHIXINGYUN_API_KEY: str = Field(default="", description="智星云 API Key")
    ZHIXINGYUN_API_SECRET: str = Field(default="", description="智星云 API Secret")

    # 阿里云 ECS
    ALIYUN_ACCESS_KEY_ID: str = Field(default="", description="阿里云 AccessKey ID")
    ALIYUN_ACCESS_KEY_SECRET: str = Field(default="", description="阿里云 AccessKey Secret")
    ALIYUN_REGION: str = Field(default="cn-shanghai", description="阿里云 Region")
    ALIYUN_SECURITY_GROUP_ID: str = Field(default="", description="安全组 ID")
    ALIYUN_VSWITCH_ID: str = Field(default="", description="交换机 ID")
    ALIYUN_IMAGE_ID: str = Field(default="", description="镜像 ID")

    # 通用云
    CLOUD_API_KEY: str = Field(default="", description="通用云 API Key")
    CLOUD_API_SECRET: str = Field(default="", description="通用云 API Secret")

    class Config:
        extra = "allow"
