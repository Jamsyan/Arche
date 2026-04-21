"""OSS plugin — 文件存储服务：本地读写、路径安全、租户隔离、元数据 CRUD。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import func, select, true
from fastapi import UploadFile

from backend.core.middleware import AppError, PermissionError

if TYPE_CHECKING:
    from backend.core.container import ServiceContainer


class StorageError(AppError):
    def __init__(self, message: str = "存储操作失败", code: str = "storage_error", status_code: int = 500):
        super().__init__(message, code, status_code)


class StorageService:
    """本地文件存储服务。"""

    def __init__(self, container: "ServiceContainer"):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]
        self.storage_root = Path(
            container.get("config").get("STORAGE_PATH", "./storage")
        ).resolve()
        self.storage_root.mkdir(parents=True, exist_ok=True)

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

        filename = file.filename or "unnamed"
        # 路径安全检查：去除 ../ 等
        if ".." in filename or "/" in filename or "\\" in filename:
            raise AppError("文件名包含非法字符", code="invalid_filename", status_code=400)

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

            # 删除物理文件
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

    # --- 存储统计 ---
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
