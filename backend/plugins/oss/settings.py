"""OSS plugin settings."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class OssSettings(BaseSettings):
    """阿里云 OSS 配置。"""

    OSS_ENDPOINT: str = Field(default="", description="OSS Endpoint")
    OSS_ACCESS_KEY_ID: str = Field(default="", description="AccessKey ID")
    OSS_ACCESS_KEY_SECRET: str = Field(default="", description="AccessKey Secret")
    OSS_BUCKET_NAME: str = Field(default="veil-cold", description="Bucket 名称")
    OSS_GLOBAL_RATE_LIMIT_BYTES: int = Field(
        default=10 * 1024 * 1024, description="全局速率限制 (bytes/s)"
    )
    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO 服务地址")
    MINIO_ROOT_USER: str = Field(default="veiladmin", description="MinIO 用户名")
    MINIO_ROOT_PASSWORD: str = Field(default="veiladmin123", description="MinIO 密码")
    MINIO_SECURE: bool = Field(default=False, description="MinIO 是否启用 TLS")

    class Config:
        extra = "allow"
