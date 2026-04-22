"""Cloud Integration plugin — 业务逻辑：Provider 管理、SSH 部署、费用计算、产物回传。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select

from backend.core.middleware import AppError

from .models import TrainingJob, TrainingInstance, TrainingCost
from .providers.registry import get_provider

VALID_JOB_STATUSES = {"pending", "running", "completed", "failed", "cancelled"}
VALID_INSTANCE_STATUSES = {"pending", "running", "stopped", "failed"}


class CloudTrainingService:
    """云训练服务：训练任务 CRUD、Provider 管理、SSH 部署、费用计算。"""

    def __init__(self, container):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]

        # Provider（延迟初始化）
        self._provider = None
        self._ssh_executor = None
        self._artifact_manager = None

    def _get_provider(self):
        """获取当前配置的 Provider 实例。"""
        if self._provider is not None:
            return self._provider

        config = self.container.get("config")
        provider_name = config.get("CLOUD_PROVIDER", "mock")

        if provider_name == "aliyun":
            credentials = {
                "access_key_id": config.get_required("ALIYUN_ACCESS_KEY_ID"),
                "access_key_secret": config.get_required("ALIYUN_ACCESS_KEY_SECRET"),
                "region": config.get("ALIYUN_REGION", "cn-shanghai"),
                "security_group_id": config.get("ALIYUN_SECURITY_GROUP_ID", ""),
                "vswitch_id": config.get("ALIYUN_VSWITCH_ID", ""),
                "image_id": config.get("ALIYUN_IMAGE_ID", ""),
            }
        else:
            credentials = {
                "api_key": config.get("CLOUD_API_KEY", ""),
                "api_secret": config.get("CLOUD_API_SECRET", ""),
            }

        self._provider = get_provider(provider_name, credentials)
        return self._provider

    def _get_ssh(self):
        """获取 SSH 执行器。"""
        if self._ssh_executor is None:
            from backend.plugins.cloud_integration.deploy.ssh_executor import SSHExecutor
            self._ssh_executor = SSHExecutor()
        return self._ssh_executor

    def _get_artifact_manager(self):
        """获取产物管理器。"""
        if self._artifact_manager is None:
            from backend.plugins.cloud_integration.deploy.artifact_manager import ArtifactManager
            self._artifact_manager = ArtifactManager(self._get_ssh())
        return self._artifact_manager

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
            # 尝试通过 SSH 读取日志
            try:
                ssh = self._get_ssh()
                # 获取该任务的运行实例
                async with self.session_factory() as session:
                    inst_result = await session.execute(
                        select(TrainingInstance)
                        .where(
                            TrainingInstance.job_id == job_id,
                            TrainingInstance.status == "running",
                        )
                    )
                    inst = inst_result.scalar_one_or_none()

                if inst and inst.ssh_host:
                    conn_key = f"{inst.ssh_host}:{inst.ssh_port}"
                    await ssh.connect(
                        host=inst.ssh_host,
                        port=inst.ssh_port,
                        user=inst.ssh_user or "root",
                        key_path=inst.ssh_key_path,
                    )
                    log_content = await ssh.execute(conn_key, f"tail -n {lines} {job.logs_path}")
                    await ssh.close(conn_key)
                else:
                    log_content = f"日志文件路径: {job.logs_path}（无运行中的实例）"
            except Exception as e:
                log_content = f"日志读取失败: {e}"

        return {
            "job_id": str(job_id),
            "logs_path": job.logs_path,
            "content": log_content,
            "lines": lines,
        }

    # --- 费用查询 ---

    async def get_costs(
        self,
        job_id: uuid.UUID | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        """查询训练费用。"""
        async with self.session_factory() as session:
            query = select(TrainingCost)
            if job_id:
                query = query.where(TrainingCost.job_id == job_id)

            result = await session.execute(query)
            costs = result.scalars().all()

            total = sum(c.total_cost for c in costs)
            breakdown = []
            for c in costs:
                breakdown.append({
                    "instance_id": str(c.instance_id),
                    "provider": c.provider,
                    "gpu_type": c.gpu_type,
                    "hourly_rate": c.hourly_rate,
                    "duration_hours": round(c.duration_hours, 2),
                    "total_cost": c.total_cost,
                    "currency": c.currency,
                    "recorded_at": c.recorded_at.isoformat() if c.recorded_at else None,
                })

            return {
                "total_cost": round(total, 2),
                "currency": "CNY",
                "instance_count": len(breakdown),
                "breakdown": breakdown,
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
        provider: str = "mock",
    ) -> dict:
        """为训练任务创建训练实例。"""
        async with self.session_factory() as session:
            job_result = await session.execute(
                select(TrainingJob).where(TrainingJob.id == job_id)
            )
            job = job_result.scalar_one_or_none()
            if not job:
                raise AppError("训练任务不存在", code="job_not_found", status_code=404)

        # 调用 Provider 创建实例
        cloud_provider = self._get_provider()
        try:
            remote = await cloud_provider.create_instance(
                job_id=str(job_id),
                config={"gpu_type": gpu_type, "gpu_count": 1},
            )
        except Exception as e:
            raise AppError(f"Provider 创建实例失败: {e}", code="provider_error", status_code=502)

        async with self.session_factory() as session:
            instance = TrainingInstance(
                job_id=job_id,
                provider=provider,
                provider_instance_id=remote.get("instance_id", ""),
                instance_name=instance_name,
                gpu_type=gpu_type,
                gpu_count=remote.get("gpu_count", 1),
                ssh_host=remote.get("host"),
                ssh_port=remote.get("port", 22),
                ssh_user=remote.get("user", "root"),
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

            # 调用 Provider 启动
            cloud_provider = self._get_provider()
            if instance.provider_instance_id:
                await cloud_provider.start_instance(instance.provider_instance_id)

            instance.status = "running"
            instance.started_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(instance)
            return self._instance_to_dict(instance)

    async def stop_instance(self, instance_id: uuid.UUID) -> dict:
        """停止训练实例（running -> stopped），计算并记录费用。"""
        from .cost import calculator

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

            # 调用 Provider 停止
            cloud_provider = self._get_provider()
            if instance.provider_instance_id:
                await cloud_provider.stop_instance(instance.provider_instance_id)

            instance.status = "stopped"
            instance.stopped_at = datetime.now(timezone.utc)

            # 计算费用
            cost = calculator.calculate_instance_cost(
                started_at=instance.started_at,
                stopped_at=instance.stopped_at,
                provider=instance.provider,
                gpu_type=instance.gpu_type,
            )
            rate = calculator.calculate_rate(instance.provider, instance.gpu_type)

            # 记录费用
            cost_record = TrainingCost(
                job_id=instance.job_id,
                instance_id=instance_id,
                provider=instance.provider,
                gpu_type=instance.gpu_type,
                hourly_rate=rate,
                duration_hours=(instance.stopped_at - instance.started_at).total_seconds() / 3600 if instance.started_at else 0,
                total_cost=cost,
            )
            session.add(cost_record)
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
            "total_cost": job.total_cost,
            "artifacts": job.artifacts,
            "artifact_verified": bool(job.artifact_verified),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }

    def _instance_to_dict(self, instance: TrainingInstance) -> dict:
        return {
            "id": str(instance.id),
            "job_id": str(instance.job_id),
            "provider": instance.provider,
            "provider_instance_id": instance.provider_instance_id,
            "instance_name": instance.instance_name,
            "gpu_type": instance.gpu_type,
            "gpu_count": instance.gpu_count,
            "ssh_host": instance.ssh_host,
            "ssh_port": instance.ssh_port,
            "ssh_user": instance.ssh_user,
            "status": instance.status,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "stopped_at": instance.stopped_at.isoformat() if instance.stopped_at else None,
        }
