"""OSS plugin — 文件存储服务：流式读写、后端解耦、动态配额、限速、租户隔离。"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator

from sqlalchemy import func, select, true
from fastapi import UploadFile

from backend.core.middleware import AppError, PermissionError

if TYPE_CHECKING:
    from backend.core.container import ServiceContainer

logger = logging.getLogger(__name__)

# === 常量 ===
DEFAULT_P1_QUOTA_BYTES = 1 * 1024**3  # 1GB 默认配额
DEFAULT_MAX_FILE_SIZE = 50 * 1024**2  # 50MB 单文件上限
CHUNK_SIZE = 64 * 1024  # 64KB 分块
ALLOWED_MIME_TYPES = {
    # 图片
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    # 文档
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    # 数据
    "application/json",
    "application/xml",
    "application/octet-stream",
    # 压缩
    "application/zip",
    "application/gzip",
    "application/x-tar",
    # 代码
    "text/x-python",
    "text/x-java-source",
    "text/javascript",
    "text/css",
    "text/html",
}


class StorageError(AppError):
    def __init__(
        self,
        message: str = "存储操作失败",
        code: str = "storage_error",
        status_code: int = 500,
    ):
        super().__init__(message, code, status_code)


class StorageService:
    """文件存储服务：本地/云端后端解耦、流式上传、动态配额、限速。"""

    def __init__(self, container: "ServiceContainer"):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]
        self.storage_root = Path(
            container.get("config").get("STORAGE_PATH", "./storage")
        ).resolve()
        self.storage_root.mkdir(parents=True, exist_ok=True)

        # 从容器获取限速器
        self._rate_limiter = container.get("oss_rate_limiter")

        # 延迟初始化阿里云后端
        self._aliyun_backend = None

    def _get_local_backend(self):
        """获取本地存储后端。"""
        from backend.plugins.oss.backends import LocalBackend

        return LocalBackend()

    def _get_aliyun_backend(self):
        """获取阿里云存储后端，配置未填写时返回 None。"""
        if self._aliyun_backend is not None:
            return self._aliyun_backend

        config = self.container.get("config")
        if config.get("OSS_ACCESS_KEY_ID") and config.get("OSS_ACCESS_KEY_SECRET"):
            from backend.plugins.oss.aliyun import CloudStorageService
            from backend.plugins.oss.backends import AliyunBackend

            cloud = CloudStorageService(self.container)
            self._aliyun_backend = AliyunBackend(cloud)
        return self._aliyun_backend

    # --- 路径安全 ---
    def _safe_path(self, relative: Path) -> Path:
        """校验路径，确保不逃逸出沙箱。"""
        resolved = (self.storage_root / relative).resolve()
        if not str(resolved).startswith(str(self.storage_root)):
            raise AppError("非法路径", code="path_traversal", status_code=400)
        return resolved

    def _user_path(self, user_id: uuid.UUID, filename: str) -> Path:
        return Path("users") / str(user_id) / filename

    def _external_path(self, tenant_id: str, filename: str) -> Path:
        return Path("external") / tenant_id / filename

    def _p1_path(self, user_id: uuid.UUID, filename: str) -> Path:
        return Path("p1") / str(user_id) / filename

    # --- 文件验证 ---
    def _validate_mime_type(self, file: UploadFile) -> None:
        mime_type = file.content_type or ""
        if mime_type and mime_type not in ALLOWED_MIME_TYPES:
            raise AppError(
                f"不支持的文件类型: {mime_type}",
                code="file_type_not_allowed",
                status_code=415,
            )

    def _validate_filename(self, filename: str) -> None:
        if ".." in filename or "/" in filename or "\\" in filename:
            raise AppError(
                "文件名包含非法字符", code="invalid_filename", status_code=400
            )

    # --- 配额管理 ---
    async def _get_user_quota_bytes(self, user_id: uuid.UUID) -> int:
        """获取用户配额上限（字节）。"""
        from backend.plugins.oss.models import UserOSSQuota

        config = self.container.get("config")
        default_quota = int(
            config.get("DEFAULT_P1_QUOTA_BYTES", str(DEFAULT_P1_QUOTA_BYTES))
        )

        async with self.session_factory() as session:
            result = await session.execute(
                select(UserOSSQuota).where(UserOSSQuota.user_id == user_id)
            )
            record = result.scalar_one_or_none()
            if record:
                return record.quota_bytes
        return default_quota

    async def _get_used_bytes(self, user_id: uuid.UUID) -> int:
        """获取用户已用存储（字节）。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(func.sum(OSSFile.size)).where(OSSFile.owner_id == user_id)
            )
            return result.scalar() or 0

    async def _check_quota(self, user_id: uuid.UUID, additional_bytes: int) -> None:
        """检查配额，超出则抛出异常。"""
        quota = await self._get_user_quota_bytes(user_id)
        used = await self._get_used_bytes(user_id)
        if used + additional_bytes > quota:
            raise AppError(
                f"存储空间不足（已用 {used / 1024**3:.2f}GB / 配额 {quota / 1024**3:.2f}GB）",
                code="quota_exceeded",
                status_code=413,
            )

    async def get_p1_quota_used(self, user_id: uuid.UUID) -> dict:
        """获取用户存储配额使用情况。"""
        quota_bytes = await self._get_user_quota_bytes(user_id)
        used = await self._get_used_bytes(user_id)

        return {
            "used_bytes": used,
            "used_gb": round(used / 1024**3, 2),
            "quota_bytes": quota_bytes,
            "quota_gb": round(quota_bytes / 1024**3, 2),
            "usage_percent": round(used / quota_bytes * 100, 1)
            if quota_bytes > 0
            else 0,
            "file_count": (await self._get_file_count(user_id)),
        }

    async def _get_file_count(self, user_id: uuid.UUID) -> int:
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count(OSSFile.id)).where(OSSFile.owner_id == user_id)
            )
            return result.scalar() or 0

    # --- 文件上传（流式） ---
    async def upload_file(
        self,
        file: UploadFile,
        owner_id: uuid.UUID,
        user_level: int = 5,
        is_private: bool = False,
    ) -> dict:
        """用户上传文件（流式写入 + 限速 + 配额检查）。"""
        from backend.plugins.oss.models import OSSFile

        self._validate_mime_type(file)
        filename = file.filename or "unnamed"
        self._validate_filename(filename)

        # 决定存储路径
        if user_level == 1:
            relative = self._p1_path(owner_id, filename)
        else:
            relative = self._user_path(owner_id, filename)
        target = self._safe_path(relative)

        # 预检查配额
        if user_level == 1:
            await self._check_quota(owner_id, CHUNK_SIZE)

        # 流式上传 + 限速 + 配额检查
        total_bytes = 0

        async def byte_stream() -> AsyncGenerator[bytes, None]:
            nonlocal total_bytes
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break

                # 全文件总大小限制
                if total_bytes + len(chunk) > DEFAULT_MAX_FILE_SIZE:
                    raise AppError(
                        f"文件大小超过限制 ({DEFAULT_MAX_FILE_SIZE // 1024 // 1024}MB)",
                        code="file_too_large",
                        status_code=413,
                    )

                total_bytes += len(chunk)

                # P1 配额实时检查
                if user_level == 1:
                    quota = await self._get_user_quota_bytes(owner_id)
                    used = await self._get_used_bytes(owner_id)
                    if used + total_bytes > quota:
                        raise AppError(
                            "超出存储配额", code="quota_exceeded", status_code=413
                        )

                # 限速
                if self._rate_limiter:
                    await self._rate_limiter.consume(owner_id, len(chunk))

                yield chunk

        # 流式写入
        backend = self._get_local_backend()
        target.parent.mkdir(parents=True, exist_ok=True)
        await backend.upload_stream(target, byte_stream(), total_bytes)

        # 写入数据库记录
        async with self.session_factory() as session:
            oss_file = OSSFile(
                owner_id=owner_id,
                path=str(relative),
                size=total_bytes,
                mime_type=file.content_type,
                storage_type="local",
                is_private=is_private,
            )
            session.add(oss_file)
            await session.commit()
            await session.refresh(oss_file)

        return self._to_dict(oss_file)

    # --- 文件下载（流式） ---
    async def download_file(
        self,
        file_id: uuid.UUID,
        requester_id: uuid.UUID | None,
        requester_level: int = 5,
    ) -> tuple[AsyncGenerator[bytes, None] | Path, dict, bool]:
        """下载文件，返回 (数据源, 元数据, 是否是流)。

        如果返回的是流（AsyncGenerator），调用方用 StreamingResponse 返回。
        如果返回的是 Path，调用方用 FileResponse 返回。
        """
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(select(OSSFile).where(OSSFile.id == file_id))
            oss_file = result.scalar_one_or_none()
            if not oss_file:
                raise AppError("文件不存在", code="file_not_found", status_code=404)

            if (
                oss_file.is_private
                and oss_file.owner_id != requester_id
                and requester_level > 0
            ):
                raise PermissionError("无权访问该文件")

            oss_file.last_accessed = datetime.now(timezone.utc)
            await session.commit()

        # 根据存储类型决定下载方式
        if oss_file.storage_type == "aliyun":
            aliyun = self._get_aliyun_backend()
            if not aliyun:
                raise StorageError("阿里云 OSS 未配置")
            return aliyun.download(Path(oss_file.path)), self._to_dict(oss_file), True
        else:
            local = self._get_local_backend()
            file_path = self._safe_path(Path(oss_file.path))
            if not await local.exists(file_path):
                raise StorageError("文件在存储中不存在")
            return local.download(file_path), self._to_dict(oss_file), True

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
            result = await session.execute(select(OSSFile).where(OSSFile.id == file_id))
            oss_file = result.scalar_one_or_none()
            if not oss_file:
                raise AppError("文件不存在", code="file_not_found", status_code=404)

            if oss_file.owner_id != requester_id and requester_level > 0:
                raise PermissionError("无权删除该文件")

            # 根据存储类型删除
            if oss_file.storage_type == "aliyun":
                aliyun = self._get_aliyun_backend()
                if not aliyun:
                    raise StorageError("阿里云 OSS 未配置")
                await aliyun.delete(Path(oss_file.path))
            else:
                local = self._get_local_backend()
                await local.delete(self._safe_path(Path(oss_file.path)))

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
        self._validate_filename(filename)

        relative = self._external_path(tenant_id, filename)
        target = self._safe_path(relative)

        # 流式写入
        async def byte_stream() -> AsyncGenerator[bytes, None]:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk

        local = self._get_local_backend()
        target.parent.mkdir(parents=True, exist_ok=True)
        await local.upload_stream(target, byte_stream(), 0)

        # 获取实际大小
        size = target.stat().st_size

        async with self.session_factory() as session:
            oss_file = OSSFile(
                tenant_id=tenant_id,
                path=str(relative),
                size=size,
                mime_type=file.content_type,
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
        """将超过 N 天未访问的本地文件迁移到阿里云 OSS。"""
        from backend.plugins.oss.models import OSSFile

        aliyun = self._get_aliyun_backend()
        if not aliyun:
            return 0

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        async with self.session_factory() as session:
            result = await session.execute(
                select(OSSFile).where(
                    OSSFile.storage_type == "local",
                    OSSFile.last_accessed < cutoff,
                    OSSFile.is_private,
                )
            )
            files = result.scalars().all()

        migrated = 0
        failed = 0
        for oss_file in files:
            try:
                local_path = self._safe_path(Path(oss_file.path))
                if not await self._get_local_backend().exists(local_path):
                    continue

                # 流式读取本地文件并上传到阿里云
                async def local_stream() -> AsyncGenerator[bytes, None]:
                    async for chunk in self._get_local_backend().download(local_path):
                        yield chunk

                await aliyun.upload(local_path, local_stream(), oss_file.size)

                # 更新数据库记录
                async with self.session_factory() as session:
                    result = await session.execute(
                        select(OSSFile).where(OSSFile.id == oss_file.id)
                    )
                    record = result.scalar_one()
                    record.storage_type = "aliyun"
                    await session.commit()

                # 删除本地文件
                await self._get_local_backend().delete(local_path)
                migrated += 1
            except Exception as e:
                logger.warning(f"[OSS] 冷迁移失败 file_id={oss_file.id}: {e}")
                failed += 1

        if failed > 0:
            logger.info(f"[OSS] 冷迁移: {migrated} 成功, {failed} 失败")
        return migrated

    # --- 存储统计 ---
    async def get_user_storage_used(self, user_id: uuid.UUID) -> dict:
        """获取用户存储空间使用情况。"""
        total = await self._get_used_bytes(user_id)
        count = await self._get_file_count(user_id)
        return {"total_bytes": total, "file_count": count}

    async def get_storage_stats(
        self,
        user_id: uuid.UUID | None = None,
    ) -> dict:
        """获取存储统计信息。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            if user_id:
                filter_clause = OSSFile.owner_id == user_id
            else:
                filter_clause = true()

            count_result = await session.execute(
                select(func.count(OSSFile.id)).where(filter_clause)
            )
            total_files = count_result.scalar() or 0

            size_result = await session.execute(
                select(func.sum(OSSFile.size)).where(filter_clause)
            )
            total_size = size_result.scalar() or 0

            type_result = await session.execute(
                select(
                    OSSFile.storage_type, func.count(OSSFile.id), func.sum(OSSFile.size)
                )
                .where(filter_clause)
                .group_by(OSSFile.storage_type)
            )
            by_type = {}
            for row in type_result.all():
                by_type[row[0]] = {"count": row[1], "size": row[2] or 0}

            # 磁盘实际占用（用 os.scandir 替代 rglob）
            local = self._get_local_backend()
            disk_usage = local.get_disk_usage(self.storage_root)

        return {
            "total_files": total_files,
            "total_size": total_size,
            "by_type": by_type,
            "disk_usage": disk_usage,
            "storage_root": str(self.storage_root),
        }

    # --- 管理员方法 ---
    async def update_user_quota(
        self,
        user_id: uuid.UUID,
        quota_bytes: int | None = None,
        speed_multiplier: float | None = None,
    ) -> dict:
        """更新用户配额配置（管理员调用）。"""
        from backend.plugins.oss.models import UserOSSQuota

        async with self.session_factory() as session:
            result = await session.execute(
                select(UserOSSQuota).where(UserOSSQuota.user_id == user_id)
            )
            record = result.scalar_one_or_none()

            if record:
                if quota_bytes is not None:
                    record.quota_bytes = quota_bytes
                if speed_multiplier is not None:
                    record.speed_multiplier = speed_multiplier
            else:
                record = UserOSSQuota(
                    user_id=user_id,
                    quota_bytes=quota_bytes or DEFAULT_P1_QUOTA_BYTES,
                    speed_multiplier=speed_multiplier or 1.0,
                )
                session.add(record)

            await session.commit()
            await session.refresh(record)

            # 同步更新限速器
            if speed_multiplier is not None and self._rate_limiter:
                self._rate_limiter.set_user_multiplier(user_id, speed_multiplier)

            return {
                "user_id": str(user_id),
                "quota_bytes": record.quota_bytes,
                "speed_multiplier": record.speed_multiplier,
            }

    async def list_user_quotas(self, limit: int = 50, offset: int = 0) -> dict:
        """列出用户配额（含已用统计）。"""
        from backend.plugins.oss.models import UserOSSQuota, OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(UserOSSQuota)
                .order_by(UserOSSQuota.user_id)
                .limit(limit)
                .offset(offset)
            )
            quotas = result.scalars().all()

            items = []
            for q in quotas:
                used_result = await session.execute(
                    select(func.sum(OSSFile.size)).where(OSSFile.owner_id == q.user_id)
                )
                used = used_result.scalar() or 0
                items.append(
                    {
                        "user_id": str(q.user_id),
                        "quota_bytes": q.quota_bytes,
                        "speed_multiplier": q.speed_multiplier,
                        "used_bytes": used,
                        "usage_percent": round(used / q.quota_bytes * 100, 1)
                        if q.quota_bytes > 0
                        else 0,
                    }
                )

            total_result = await session.execute(select(func.count(UserOSSQuota.id)))
            return {"items": items, "total": total_result.scalar() or 0}

    async def admin_list_files(
        self,
        user_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """管理员文件列表，可按用户过滤。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            query = (
                select(OSSFile)
                .order_by(OSSFile.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            if user_id:
                query = query.where(OSSFile.owner_id == user_id)

            result = await session.execute(query)
            files = result.scalars().all()
            return [self._to_dict(f) for f in files]

    async def admin_delete_file(self, file_id: uuid.UUID) -> None:
        """管理员删除任意文件。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(select(OSSFile).where(OSSFile.id == file_id))
            oss_file = result.scalar_one_or_none()
            if not oss_file:
                raise AppError("文件不存在", code="file_not_found", status_code=404)

            if oss_file.storage_type == "local":
                local = self._get_local_backend()
                await local.delete(self._safe_path(Path(oss_file.path)))
            elif oss_file.storage_type == "aliyun":
                aliyun = self._get_aliyun_backend()
                if aliyun:
                    await aliyun.delete(Path(oss_file.path))

            await session.delete(oss_file)
            await session.commit()

    async def get_admin_stats(self) -> dict:
        """管理员统计大盘。"""
        from backend.plugins.oss.models import OSSFile, UserOSSQuota

        async with self.session_factory() as session:
            total_files = await session.execute(select(func.count(OSSFile.id)))
            total_size = await session.execute(select(func.sum(OSSFile.size)))
            total_users = await session.execute(select(func.count(UserOSSQuota.id)))

            type_result = await session.execute(
                select(
                    OSSFile.storage_type, func.count(OSSFile.id), func.sum(OSSFile.size)
                ).group_by(OSSFile.storage_type)
            )
            by_type = {}
            for row in type_result.all():
                by_type[row[0]] = {"count": row[1], "size": row[2] or 0}

            local = self._get_local_backend()
            disk_usage = local.get_disk_usage(self.storage_root)

            return {
                "total_files": total_files.scalar() or 0,
                "total_size": total_size.scalar() or 0,
                "total_users": total_users.scalar() or 0,
                "by_type": by_type,
                "disk_usage": disk_usage,
            }

    async def get_top_users_by_storage(self, limit: int = 20) -> list[dict]:
        """按存储使用量排行的用户。"""
        from backend.plugins.oss.models import OSSFile

        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    OSSFile.owner_id,
                    func.sum(OSSFile.size).label("total"),
                    func.count(OSSFile.id).label("count"),
                )
                .where(OSSFile.owner_id.isnot(None))
                .group_by(OSSFile.owner_id)
                .order_by(func.sum(OSSFile.size).desc())
                .limit(limit)
            )
            rows = result.all()
            return [
                {"user_id": str(r[0]), "total_bytes": r[1] or 0, "file_count": r[2]}
                for r in rows
            ]

    # --- 工具方法 ---
    def _to_dict(self, oss_file) -> dict:
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
