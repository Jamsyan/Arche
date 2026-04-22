"""Storage backend abstraction — MinIO（本地对象存储）/ 阿里云 OSS 统一接口。"""

from __future__ import annotations

import io
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator

CHUNK_SIZE = 64 * 1024

if TYPE_CHECKING:
    from minio import Minio as MinioClient
    from backend.plugins.oss.aliyun import CloudStorageService


class StorageBackend(ABC):
    """存储后端抽象接口。"""

    @abstractmethod
    async def upload_stream(
        self, key: str, stream: AsyncGenerator[bytes, None], size: int
    ) -> None:
        """流式写入文件。"""
        ...

    @abstractmethod
    async def download(self, key: str) -> AsyncGenerator[bytes, None]:
        """流式读取文件，返回字节生成器。"""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """删除文件。"""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查文件是否存在。"""
        ...

    @abstractmethod
    def get_disk_usage(self) -> int:
        """获取当前桶的总使用量（字节）。"""
        ...

    @property
    @abstractmethod
    def backend_type(self) -> str:
        """返回后端类型标识，如 'minio' / 'aliyun'。"""
        ...


class MinIOBackend(StorageBackend):
    """本地 MinIO 对象存储后端（S3 兼容）。"""

    def __init__(self, client: "MinioClient", bucket: str):
        self._client = client
        self._bucket = bucket

    def _ensure_bucket(self):
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    async def upload_stream(
        self, key: str, stream: AsyncGenerator[bytes, None], size: int
    ) -> None:
        self._ensure_bucket()

        # MinIO put_object 接受类文件对象，需要收集所有 chunk
        chunks = [chunk async for chunk in stream]
        data = b"".join(chunks)
        self._client.put_object(
            self._bucket,
            key,
            io.BytesIO(data),
            length=len(data),
        )

    async def download(self, key: str) -> AsyncGenerator[bytes, None]:
        response = self._client.get_object(self._bucket, key)
        try:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk
        finally:
            response.close()
            response.release_conn()

    async def delete(self, key: str) -> None:
        self._client.remove_object(self._bucket, key)

    async def exists(self, key: str) -> bool:
        try:
            self._client.stat_object(self._bucket, key)
            return True
        except Exception:
            return False

    def get_disk_usage(self) -> int:
        """统计桶中所有对象的总大小。"""
        total = 0
        for obj in self._client.list_objects(self._bucket, recursive=True):
            total += obj.size or 0
        return total

    @property
    def backend_type(self) -> str:
        return "minio"


class AliyunBackend(StorageBackend):
    """阿里云 OSS 存储后端（远程对象存储）。"""

    def __init__(self, cloud_service: "CloudStorageService"):
        self._cloud = cloud_service

    async def upload_stream(
        self, key: str, stream: AsyncGenerator[bytes, None], size: int
    ) -> None:
        chunks = [chunk async for chunk in stream]
        content = b"".join(chunks)
        await self._cloud.upload(key, content)

    async def upload_from_file(self, key: str, local_path: Path) -> str:
        """从本地文件上传到阿里云（用于冷热迁移）。"""
        return await self._cloud.upload(key, local_path)

    async def download(self, key: str) -> AsyncGenerator[bytes, None]:
        content = await self._cloud.download_bytes(key)
        for i in range(0, len(content), CHUNK_SIZE):
            yield content[i : i + CHUNK_SIZE]

    async def delete(self, key: str) -> None:
        await self._cloud.delete(key)

    async def exists(self, key: str) -> bool:
        return await self._cloud.object_exists(key)

    def get_disk_usage(self) -> int:
        return 0

    @property
    def backend_type(self) -> str:
        return "aliyun"
