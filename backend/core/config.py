"""Configuration management — env file + env vars + required key validation."""

from __future__ import annotations

import os
from pathlib import Path


class Config:
    """Layered config: defaults < .env < environment variables."""

    def __init__(self, env_file: str = ".env"):
        self._values: dict[str, str] = {}
        self._load_env_file(env_file)
        self._load_os_environ()

    def _load_env_file(self, env_file: str) -> None:
        path = Path(env_file)
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            self._values[key.strip()] = value.strip().strip("\"'")

    def _load_os_environ(self) -> None:
        for key, value in os.environ.items():
            if (
                key in self._values
                or key.startswith("VEIL_")
                or key
                in (
                    "DATABASE_URL",
                    "SECRET_KEY",
                    "STORAGE_PATH",
                    "CORS_ORIGINS",
                    "LOG_LEVEL",
                    "LOG_FILE",
                    "CRAWLER_SEEDS",
                    "CRAWLER_STORAGE_ROOT",
                    "SENSITIVE_WORDS",
                    "MONITOR_COLLECT_INTERVAL",
                    "MINIO_ENDPOINT",
                    "MINIO_ROOT_USER",
                    "MINIO_ROOT_PASSWORD",
                    "MINIO_SECURE",
                    "OSS_ENDPOINT",
                    "OSS_BUCKET_NAME",
                    "OSS_ACCESS_KEY_ID",
                    "OSS_ACCESS_KEY_SECRET",
                    "CLOUD_PROVIDER",
                    "ZHIXINGYUN_API_KEY",
                    "ZHIXINGYUN_API_SECRET",
                    "ALIYUN_ACCESS_KEY_ID",
                    "ALIYUN_ACCESS_KEY_SECRET",
                    "ALIYUN_REGION",
                    "ALIYUN_SECURITY_GROUP_ID",
                    "ALIYUN_VSWITCH_ID",
                    "ALIYUN_IMAGE_ID",
                    "CLOUD_API_KEY",
                    "CLOUD_API_SECRET",
                    "GITHUB_TOKEN",
                    "GITHUB_API_BASE",
                    "GITHUB_RAW_BASE",
                    "GITHUB_CACHE_TTL",
                    "GITHUB_TIMEOUT",
                )
            ):
                self._values[key] = value

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._values.get(key, default)

    def get_required(self, key: str) -> str:
        value = self._values.get(key)
        if value is None:
            raise RuntimeError(f"Required config '{key}' is not set")
        return value

    def set(self, key: str, value: str) -> None:
        self._values[key] = value
