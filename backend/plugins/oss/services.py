"""OSS plugin — 文件存储服务：本地读写、路径安全、租户隔离、元数据 CRUD、阿里云冷存储、配额管理。"""

from __future__ import annotations

import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import func, select, true
from fastapi import UploadFile

from backend.core.middleware import AppError, PermissionError

if TYPE_CHECKING:
    from backend.core.container import ServiceContainer


# === 常量 ===
P1_QUOTA_BYTES = 10 * 1024**3  # 10GB
MAX_FILE_SIZE = 50 * 1024**2   # 50MB
ALLOWED_MIME_TYPES = {
    # 图片
    "image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "image/svg+xml",
    # 文档
    "application/pdf",
    "text/plain", "text/markdown", "text/csv",
    # 数据
    "application/json", "application/xml", "application/octet-stream",
    # 压缩
    "application/zip", "application/gzip", "application/x-tar",
    # 代码
    "text/x-python", "text/x-java-source", "text/javascript",
    "text/css", "text/html",
}


class StorageError(AppError):
    def __init__(self, message: str = "存储操作失败", code: str = "storage_error", status_code: int = 500):
        super().__init__(message, code, status_code)


class StorageService:
    """本地文件存储服务 + 阿里云冷存储调度。"""

    def __init__(self, container: "ServiceContainer"):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]
        self.storage_root = Path(
            container.get("config").get("STORAGE_PATH", "./storage")
        ).resolve()
        self.storage_root.mkdir(parents=True, exist_ok=True)

        # 延迟初始化阿里云服务（配置可能未填写）
        self._cloud_storage = None

    def _get_cloud_storage(self):
        """获取阿里云 OSS 服务实例，配置未填写时返回 None。"""
        if self._cloud_storage is not None:
            return self._cloud_storage

        config = self.container.get("config")
        if config.get("OSS_ACCESS_KEY_ID") and config.get("OSS_ACCESS_KEY_SECRET"):
            from backend.plugins.oss.aliyun import CloudStorageService
            self._cloud_storage = CloudStorageService(self.container)
        return self._cloud_storage

    # --- 路径安全 ---
    def _safe_path(self, relative: Path) -> Path:
        """校验路径，确保不逃逸出沙箱。"""
        resolved = (self.storage_root / relative).resolve()
        if not str(resolved).startswith(str(self.storage_root)):
            raise AppError("非法路径", code="path_traversal", status_code=400)
        return resolved

    def _user_path(self, user_id: uuid.UUID, filename: str) -> Path:
        """生成用户文件相对路径：users/{user_id}/{filename}"""
        return Path("users") / str(user_id) / filename

    def _external_path(self, tenant_id: str, filename: str) -> Path:
        """生成外部租户文件相对路径：external/{tenant_id}/{filename}"""
        return Path("external") / tenant_id / filename

    def _p1_path(self, user_id: uuid.UUID, filename: str) -> Path:
        """生成 P1 独立空间路径：p1/{user_id}/{filename}"""
        return Path("p1") / str(user_id) / filename

    # --- 文件验证 ---
    def _validate_file(self, file: UploadFile, user_level: int = 5) -> None:
        """验证文件大小和 MIME 类型。"""
        # 检查文件大小
        if file.size is not None and file.size > MAX_FILE_SIZE:
            raise AppError(
                f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)",
                code="file_too_large",
                status_code=413,
            )

        # 检查 MIME 类型
        mime_type = file.content_type or ""
        if mime_type and mime_type not in ALLOWED_MIME_TYPES:
            raise AppError(
                f"不支持的文件类型: {mime_type}",
                code="file_type_not_allowed",
                status_code=415,
            )

    async def _check_p1_quota(self, user_id: uuid.UUID, additional_bytes: int = 0) -> None:
        """检查 P1 用户配额，超出则抛出异常。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(func.sum(OSSFile.size))
                .where(OSSFile.owner_id == user_id)
            )
            used = result.scalar() or 0

        if used + additional_bytes > P1_QUOTA_BYTES:
            raise AppError(
                f"P1 存储空间已满（{used / 1024**3:.2f}GB / {P1_QUOTA_BYTES / 1024**3:.0f}GB）",
                code="quota_exceeded",
                status_code=413,
            )

    async def get_p1_quota_used(self, user_id: uuid.UUID) -> dict:
        """获取 P1 用户存储配额使用情况。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(func.sum(OSSFile.size), func.count(OSSFile.id))
                .where(OSSFile.owner_id == user_id)
            )
            row = result.one()
            used = row[0] or 0
            count = row[1] or 0

        return {
            "used_bytes": used,
            "used_gb": round(used / 1024**3, 2),
            "quota_bytes": P1_QUOTA_BYTES,
            "quota_gb": P1_QUOTA_BYTES / 1024**3,
            "usage_percent": round(used / P1_QUOTA_BYTES * 100, 1),
            "file_count": count,
        }

    # --- 文件上传 ---
    async def upload_file(
        self,
        file: UploadFile,
        owner_id: uuid.UUID,
        user_level: int = 5,
        is_private: bool = False,
    ) -> dict:
        """用户上传文件到本地存储。"""
        from backend.plugins.oss.models import OSSFile

        # 文件验证
        self._validate_file(file, user_level)

        filename = file.filename or "unnamed"
        # 路径安全检查：去除 ../ 等
        if ".." in filename or "/" in filename or "\\" in filename:
            raise AppError("文件名包含非法字符", code="invalid_filename", status_code=400)

        # P1 配额检查
        if user_level == 1:
            content_preview = await file.read()
            await file.seek(0)  # 重置文件指针
            await self._check_p1_quota(owner_id, additional_bytes=len(content_preview))

        # 根据用户等级决定存储位置
        if user_level == 1:
            relative = self._p1_path(owner_id, filename)
        else:
            relative = self._user_path(owner_id, filename)

        target = self._safe_path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)

        # 读取文件内容并写入
        content = await file.read()
        target.write_bytes(content)

        # 读取 mime_type
        mime_type = file.content_type

        # 写入数据库记录
        async with self.session_factory() as session:
            oss_file = OSSFile(
                owner_id=owner_id,
                path=str(relative),
                size=len(content),
                mime_type=mime_type,
                storage_type="local",
                is_private=is_private,
            )
            session.add(oss_file)
            await session.commit()
            await session.refresh(oss_file)

        return self._to_dict(oss_file)

    # --- 文件下载 ---
    async def download_file(
        self,
        file_id: uuid.UUID,
        requester_id: uuid.UUID | None,
        requester_level: int = 5,
    ) -> tuple[Path, dict]:
        """下载文件，返回文件路径和元数据。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(OSSFile).where(OSSFile.id == file_id)
            )
            oss_file = result.scalar_one_or_none()
            if not oss_file:
                raise AppError("文件不存在", code="file_not_found", status_code=404)

            # 权限检查：私有文件仅 owner 或 P0 可访问
            if oss_file.is_private and oss_file.owner_id != requester_id and requester_level > 0:
                raise PermissionError("无权访问该文件")

            # 更新 last_accessed
            oss_file.last_accessed = datetime.now(timezone.utc)
            await session.commit()

        # 根据存储类型决定下载方式
        if oss_file.storage_type == "aliyun":
            cloud = self._get_cloud_storage()
            if not cloud:
                raise StorageError("阿里云 OSS 未配置")
            # 下载到临时文件
            tmp_dir = Path(tempfile.gettempdir()) / "veil_oss"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            tmp_path = tmp_dir / oss_file.path.rsplit("/", 1)[-1]
            await cloud.download(oss_file.path, tmp_path)
            file_path = tmp_path
        else:
            file_path = self._safe_path(Path(oss_file.path))
            if not file_path.exists():
                raise StorageError("文件在存储中不存在")

        return file_path, self._to_dict(oss_file)

    # --- 文件删除 ---
    async def delete_file(
        self,
        file_id: uuid.UUID,
        requester_id: uuid.UUID,
        requester_level: int = 5,
    ) -> None:
        """删除文件，仅作者本人或 P0 可删除。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(OSSFile).where(OSSFile.id == file_id)
            )
            oss_file = result.scalar_one_or_none()
            if not oss_file:
                raise AppError("文件不存在", code="file_not_found", status_code=404)

            # 权限检查：作者本人或 P0
            if oss_file.owner_id != requester_id and requester_level > 0:
                raise PermissionError("无权删除该文件")

            # 根据存储类型删除
            if oss_file.storage_type == "aliyun":
                cloud = self._get_cloud_storage()
                if not cloud:
                    raise StorageError("阿里云 OSS 未配置")
                await cloud.delete(oss_file.path)
            else:
                file_path = self._safe_path(Path(oss_file.path))
                if file_path.exists():
                    file_path.unlink()

            # 删除数据库记录
            await session.delete(oss_file)
            await session.commit()

    # --- 我的文件列表 ---
    async def list_my_files(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """获取当前用户的文件列表。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(OSSFile)
                .where(OSSFile.owner_id == user_id)
                .order_by(OSSFile.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            files = result.scalars().all()
            return [self._to_dict(f) for f in files]

    # --- 外部写入 ---
    async def external_upload(
        self,
        file: UploadFile,
        tenant_id: str,
    ) -> dict:
        """外部租户写入文件。"""
        from backend.plugins.oss.models import OSSFile

        filename = file.filename or "unnamed"
        if ".." in filename or "/" in filename or "\\" in filename:
            raise AppError("文件名包含非法字符", code="invalid_filename", status_code=400)

        relative = self._external_path(tenant_id, filename)
        target = self._safe_path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        target.write_bytes(content)

        mime_type = file.content_type

        async with self.session_factory() as session:
            oss_file = OSSFile(
                tenant_id=tenant_id,
                path=str(relative),
                size=len(content),
                mime_type=mime_type,
                storage_type="local",
            )
            session.add(oss_file)
            await session.commit()
            await session.refresh(oss_file)

        return self._to_dict(oss_file)

    # --- 外部文件列表 ---
    async def list_external_files(
        self,
        tenant_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """获取指定租户的文件列表。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(OSSFile)
                .where(OSSFile.tenant_id == tenant_id)
                .order_by(OSSFile.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            files = result.scalars().all()
            return [self._to_dict(f) for f in files]

    # --- 冷热分层调度 ---
    async def evict_cold_files(self, days: int = 7) -> int:
        """将超过 N 天未访问的本地文件迁移到阿里云 OSS。

        Returns:
            迁移成功的文件数
        """
        from backend.plugins.oss.models import OSSFile

        cloud = self._get_cloud_storage()
        if not cloud:
            return 0

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        async with self.session_factory() as session:
            result = await session.execute(
                select(OSSFile)
                .where(
                    OSSFile.storage_type == "local",
                    OSSFile.last_accessed < cutoff,
                    OSSFile.is_private == True,  # 仅个人私有文件
                )
            )
            files = result.scalars().all()

        migrated = 0
        for oss_file in files:
            try:
                local_path = self._safe_path(Path(oss_file.path))
                if not local_path.exists():
                    continue

                # 上传到阿里云
                object_key = oss_file.path
                await cloud.upload(object_key, local_path)

                # 更新数据库记录
                async with self.session_factory() as session:
                    result = await session.execute(
                        select(OSSFile).where(OSSFile.id == oss_file.id)
                    )
                    record = result.scalar_one()
                    record.storage_type = "aliyun"
                    await session.commit()

                # 删除本地文件
                local_path.unlink()
                migrated += 1
            except Exception:
                # 单个文件失败不影响其他文件
                continue

        return migrated

    # --- 用户存储空间统计 ---
    async def get_user_storage_used(self, user_id: uuid.UUID) -> dict:
        """获取用户存储空间使用情况。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(func.sum(OSSFile.size), func.count(OSSFile.id))
                .where(OSSFile.owner_id == user_id)
            )
            row = result.one()
            return {
                "total_bytes": row[0] or 0,
                "file_count": row[1] or 0,
            }

    async def get_storage_stats(
        self,
        user_id: uuid.UUID | None = None,
    ) -> dict:
        """获取存储统计信息。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            # 构建过滤条件
            if user_id:
                filter_clause = OSSFile.owner_id == user_id
            else:
                filter_clause = true()

            # 总文件数
            count_result = await session.execute(
                select(func.count(OSSFile.id)).where(filter_clause)
            )
            total_files = count_result.scalar() or 0

            # 总大小
            size_result = await session.execute(
                select(func.sum(OSSFile.size)).where(filter_clause)
            )
            total_size = size_result.scalar() or 0

            # 按存储类型统计
            type_result = await session.execute(
                select(OSSFile.storage_type, func.count(OSSFile.id), func.sum(OSSFile.size))
                .where(filter_clause)
                .group_by(OSSFile.storage_type)
            )
            by_type = {}
            for row in type_result.all():
                by_type[row[0]] = {"count": row[1], "size": row[2] or 0}

            # 磁盘实际占用
            disk_usage = 0
            if self.storage_root.exists():
                for p in self.storage_root.rglob("*"):
                    if p.is_file():
                        disk_usage += p.stat().st_size

        return {
            "total_files": total_files,
            "total_size": total_size,
            "by_type": by_type,
            "disk_usage": disk_usage,
            "storage_root": str(self.storage_root),
        }

    # --- 工具方法 ---
    def _to_dict(self, oss_file) -> dict:
        """将 OSSFile 转为字典。"""
        def _format_dt(dt):
            if dt is None:
                return None
            if isinstance(dt, str):
                return dt
            return dt.isoformat()

        return {
            "id": str(oss_file.id),
            "owner_id": str(oss_file.owner_id) if oss_file.owner_id else None,
            "tenant_id": oss_file.tenant_id,
            "path": oss_file.path,
            "size": oss_file.size,
            "mime_type": oss_file.mime_type,
            "storage_type": oss_file.storage_type,
            "is_private": oss_file.is_private,
            "created_at": _format_dt(oss_file.created_at),
            "last_accessed": _format_dt(oss_file.last_accessed),
        }
