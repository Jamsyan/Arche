"""部署 Webhook 插件设置。"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class DeployWebhookSettings(BaseSettings):
    """部署 Webhook 配置。"""

    DEPLOY_SCRIPT: str = Field(
        default="/home/admin/arche/deploy.sh", description="部署脚本路径"
    )
    DEPLOY_TOKEN: str = Field(default="", description="部署 Webhook Token")

    class Config:
        extra = "allow"
