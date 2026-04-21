"""Cloud Integration plugin — 业务逻辑。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select

from backend.core.middleware import AppError

from .models import TrainingJob, TrainingInstance

VALID_JOB_STATUSES = {"pending", "running", "completed", "failed", "cancelled"}
VALID_INSTANCE_STATUSES = {"pending", "running", "stopped", "failed"}


class CloudTrainingService:
    """云训练服务：训练任务 CRUD、启动/停止、实例管理、日志查看。"""

    def __init__(self, container):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]

    # --- 任务状态机 ---

    VALID_TRANSITIONS = {
        "pending": {"running", "cancelled"},
        "running": {"completed", "failed", "cancelled"},
        "completed": set(),
        "failed": set(),
        "cancelled": set(),
    }

    def _transition(self, current: str, target: str) -> None:
        if target not in self.VALID_TRANSITIONS.get(current, set()):
            raise AppError(
                f"无法从状态 '{current}' 转换到 '{target}'",
                code="invalid_transition",
                status_code=400,
            )

    # --- 任务 CRUD ---

    async def list_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
        creator_id: uuid.UUID | None = None,
    ) -> dict:
        """获取训练任务列表（分页）。"""
        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            query = select(TrainingJob)
            if status_filter:
                query = query.where(TrainingJob.status == status_filter)
            if creator_id:
                query = query.where(TrainingJob.creator_id == creator_id)

            count_query = select(func.count()).select_from(TrainingJob)
            if status_filter:
                count_query = count_query.where(TrainingJob.status == status_filter)
            if creator_id:
                count_query = count_query.where(TrainingJob.creator_id == creator_id)
            total = (await session.execute(count_query)).scalar_one()

            query = query.order_by(TrainingJob.created_at.desc())
            query = query.offset(offset).limit(page_size)

            jobs = (await session.execute(query)).scalars().all()

            return {
                "items": [self._job_to_dict(j) for j in jobs],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def get_job(self, job_id: uuid.UUID) -> dict:
        """获取训练任务详情。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)
            return self._job_to_dict(job)

    async def create_job(
        self,
        creator_id: uuid.UUID,
        name: str,
        model_config: dict,
    ) -> dict:
        """创建新的训练任务，初始状态为 pending。"""
        async with self.session_factory() as session:
            job = TrainingJob(
                creator_id=creator_id,
                name=name,
                model_config=model_config,
                status="pending",
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return self._job_to_dict(job)

    async def delete_job(self, job_id: uuid.UUID) -> None:
        """删除训练任务（仅 pending 或 cancelled 状态）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)
            if job.status not in ("pending", "cancelled"):
                raise AppError(
                    f"无法删除状态为 '{job.status}' 的任务",
                    code="invalid_status",
                    status_code=400,
                )

            # 删除关联实例
            await session.execute(
                TrainingInstance.__table__.delete().where(
                    TrainingInstance.job_id == job_id
                )
            )
            await session.delete(job)
            await session.commit()

    # --- 任务状态操作 ---

    async def start_job(self, job_id: uuid.UUID) -> dict:
        """启动训练任务（pending -> running）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)

            self._transition(job.status, "running")
            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(job)
            return self._job_to_dict(job)

    async def stop_job(self, job_id: uuid.UUID) -> dict:
        """停止训练任务（running -> cancelled）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)

            self._transition(job.status, "cancelled")
            job.status = "cancelled"
            job.completed_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(job)
            return self._job_to_dict(job)

    async def complete_job(self, job_id: uuid.UUID, result_path: str | None = None) -> dict:
        """标记任务完成（running -> completed）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)

            self._transition(job.status, "completed")
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            if result_path:
                job.result_path = result_path
            await session.commit()
            await session.refresh(job)
            return self._job_to_dict(job)

    async def fail_job(self, job_id: uuid.UUID, error_message: str) -> dict:
        """标记任务失败（running -> failed）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)

            self._transition(job.status, "failed")
            job.status = "failed"
            job.completed_at = datetime.now(timezone.utc)
            job.error_message = error_message
            await session.commit()
            await session.refresh(job)
            return self._job_to_dict(job)

    # --- 训练日志 ---

    async def get_job_logs(self, job_id: uuid.UUID, lines: int = 100) -> dict:
        """获取训练任务日志。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)

            log_content = ""
            if job.logs_path:
                # TODO: 实际从存储读取日志文件
                log_content = f"日志文件路径: {job.logs_path}"

            return {
                "job_id": str(job_id),
                "logs_path": job.logs_path,
                "content": log_content,
                "lines": lines,
            }

    # --- 训练实例管理 ---

    async def list_instances(
        self,
        job_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """获取训练任务的实例列表。"""
        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            count_result = await session.execute(
                select(func.count()).where(TrainingInstance.job_id == job_id)
            )
            total = count_result.scalar_one()

            result = await session.execute(
                select(TrainingInstance)
                .where(TrainingInstance.job_id == job_id)
                .order_by(TrainingInstance.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            instances = result.scalars().all()

            return {
                "items": [self._instance_to_dict(i) for i in instances],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def create_instance(
        self,
        job_id: uuid.UUID,
        instance_name: str,
        gpu_type: str,
    ) -> dict:
        """为训练任务创建训练实例。"""
        async with self.session_factory() as session:
            job_result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = job_result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)

            instance = TrainingInstance(
                job_id=job_id,
                instance_name=instance_name,
                gpu_type=gpu_type,
                status="pending",
            )
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return self._instance_to_dict(instance)

    async def start_instance(self, instance_id: uuid.UUID) -> dict:
        """启动训练实例（pending -> running）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingInstance).where(TrainingInstance.id == instance_id)
            )
            instance = result.scalar_one_or_none()
            if not instance:
                raise AppError(
                    "训练实例不存在", code="instance_not_found", status_code=404
                )

            if instance.status != "pending":
                raise AppError(
                    f"实例状态为 '{instance.status}'，无法启动",
                    code="invalid_status",
                    status_code=400,
                )

            instance.status = "running"
            instance.started_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(instance)
            return self._instance_to_dict(instance)

    async def stop_instance(self, instance_id: uuid.UUID) -> dict:
        """停止训练实例（running -> stopped）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(TrainingInstance).where(TrainingInstance.id == instance_id)
            )
            instance = result.scalar_one_or_none()
            if not instance:
                raise AppError(
                    "训练实例不存在", code="instance_not_found", status_code=404
                )

            if instance.status != "running":
                raise AppError(
                    f"实例状态为 '{instance.status}'，无法停止",
                    code="invalid_status",
                    status_code=400,
                )

            instance.status = "stopped"
            instance.stopped_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(instance)
            return self._instance_to_dict(instance)

    # --- 数据转换 ---

    def _job_to_dict(self, job: TrainingJob) -> dict:
        return {
            "id": str(job.id),
            "name": job.name,
            "creator_id": str(job.creator_id),
            "model_config": job.model_config,
            "status": job.status,
            "logs_path": job.logs_path,
            "result_path": job.result_path,
            "error_message": job.error_message,
            "gpu_hours": job.gpu_hours,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }

    def _instance_to_dict(self, instance: TrainingInstance) -> dict:
        return {
            "id": str(instance.id),
            "job_id": str(instance.job_id),
            "instance_name": instance.instance_name,
            "gpu_type": instance.gpu_type,
            "status": instance.status,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "stopped_at": instance.stopped_at.isoformat() if instance.stopped_at else None,
        }
