"""Storage backend abstraction — 本地/阿里云统一接口，流式读写。"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from backend.plugins.oss.aliyun import CloudStorageService


class StorageBackend(ABC):
    """存储后端抽象接口。"""

    @abstractmethod
    async def upload_stream(
        self, path: Path, stream: AsyncGenerator[bytes, None], size: int
    ) -> None:
        """流式写入文件。"""
        ...

    @abstractmethod
    async def download(self, path: Path) -> AsyncGenerator[bytes, None]:
        """流式读取文件，返回字节生成器。"""
        ...

    @abstractmethod
    async def delete(self, path: Path) -> None:
        """删除文件。"""
        ...

    @abstractmethod
    async def exists(self, path: Path) -> bool:
        """检查文件是否存在。"""
        ...

    @abstractmethod
    def get_disk_usage(self, root: Path) -> int:
        """获取根目录下所有文件的总大小（用 os.scandir 迭代，比 rglob 快）。"""
        ...

    @property
    @abstractmethod
    def backend_type(self) -> str:
        """返回后端类型标识，如 'local' / 'aliyun'。"""
        ...


class LocalBackend(StorageBackend):
    """本地文件系统存储后端，64KB chunk 流式读写。"""

    CHUNK = 64 * 1024

    async def upload_stream(
        self, path: Path, stream: AsyncGenerator[bytes, None], size: int
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            async for chunk in stream:
                f.write(chunk)

    async def download(self, path: Path) -> AsyncGenerator[bytes, None]:
        with open(path, "rb") as f:
            while chunk := f.read(self.CHUNK):
                yield chunk

    async def delete(self, path: Path) -> None:
        if path.exists():
            path.unlink()

    async def exists(self, path: Path) -> bool:
        return path.exists()

    def get_disk_usage(self, root: Path) -> int:
        total = 0
        with os.scandir(root) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += self._walk_dir(Path(entry.path))
        return total

    def _walk_dir(self, directory: Path) -> int:
        total = 0
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += self._walk_dir(Path(entry.path))
        except OSError:
            pass
        return total

    @property
    def backend_type(self) -> str:
        return "local"


class AliyunBackend(StorageBackend):
    """阿里云 OSS 存储后端（冷存储），包装 CloudStorageService。"""

    CHUNK = 64 * 1024

    def __init__(self, cloud_service: "CloudStorageService"):
        self._cloud = cloud_service

    async def upload_stream(
        self, path: Path, stream: AsyncGenerator[bytes, None], size: int
    ) -> None:
        chunks = [chunk async for chunk in stream]
        content = b"".join(chunks)
        await self._cloud.upload(str(path), content)

    async def upload_from_file(self, object_key: str, local_path: Path) -> str:
        """从本地文件上传到阿里云（用于冷热迁移）。"""
        return await self._cloud.upload(object_key, local_path)

    async def download(self, path: Path) -> AsyncGenerator[bytes, None]:
        content = await self._cloud.download_bytes(str(path))
        for i in range(0, len(content), self.CHUNK):
            yield content[i : i + self.CHUNK]

    async def delete(self, path: Path) -> None:
        await self._cloud.delete(str(path))

    async def exists(self, path: Path) -> bool:
        return await self._cloud.object_exists(str(path))

    def get_disk_usage(self, root: Path) -> int:
        return 0

    @property
    def backend_type(self) -> str:
        return "aliyun"
