"""Cloud Integration plugin — 数据模型。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.db import Base


class TrainingJob(Base):
    """训练任务表。"""

    __tablename__ = "training_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    model_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    logs_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    result_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    gpu_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    artifacts: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    artifact_verified: Mapped[bool] = mapped_column(Integer, nullable=False, default=0)

    # 仓库与编排字段
    repo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    repo_branch: Mapped[str | None] = mapped_column(
        String(256), nullable=True, server_default="main"
    )
    repo_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    dataset_config: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=dict
    )
    training_script: Mapped[str | None] = mapped_column(String(512), nullable=True)
    log_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    log_pattern: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        server_default=r"epoch\s+(\d+).*?loss\s*[:=]\s*([\d.]+)",
    )
    requirements_file: Mapped[str | None] = mapped_column(
        String(512), nullable=True, server_default="requirements.txt"
    )
    progress_info: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=dict
    )
    orchestrator_step: Mapped[str | None] = mapped_column(
        String(64), nullable=True, server_default="idle"
    )
    orchestrator_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TrainingInstance(Base):
    """训练实例表。"""

    __tablename__ = "training_instances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_jobs.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="mock")
    provider_instance_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    instance_name: Mapped[str] = mapped_column(String(256), nullable=False)
    gpu_type: Mapped[str] = mapped_column(String(64), nullable=False)
    gpu_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ssh_host: Mapped[str | None] = mapped_column(String(256), nullable=True)
    ssh_port: Mapped[int] = mapped_column(Integer, nullable=False, default=22)
    ssh_user: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ssh_key_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ssh_password: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    last_heartbeat: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    stopped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TrainingCost(Base):
    """训练费用记录表。"""

    __tablename__ = "training_costs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_jobs.id"), nullable=False
    )
    instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_instances.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    gpu_type: Mapped[str] = mapped_column(String(64), nullable=False)
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="CNY")
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TrainingTaskStep(Base):
    """训练任务编排步骤记录表。"""

    __tablename__ = "training_task_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_jobs.id"), nullable=False
    )
    step_name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_data: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
