"""云工作台种子数据。

用法：uv run python -m backend.scripts.seed_cloud_data
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from backend.plugins.cloud_integration.models import (
    TrainingJob,
    TrainingTaskStep,
    Dataset,
    CodeRepo,
    Artifact,
)
from backend.core.db import init_db, Base


async def seed_cloud_data():
    """生成云工作台测试数据。"""
    import os

    # 使用与后端相同的数据库 URL
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")
    engine, _ = init_db(db_url)

    # 确保表存在
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        # 测试用户 ID（使用 auth 插件中默认的 admin 用户 ID）
        admin_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        # --- 代码仓库 ---
        repo1 = CodeRepo(
            id=uuid.uuid4(),
            name="LLM 微调项目",
            git_url="https://github.com/example/llm-finetune.git",
            git_branch="main",
            git_token=None,
            created_by=admin_id,
            created_at=datetime.now() - timedelta(days=5),
        )
        repo2 = CodeRepo(
            id=uuid.uuid4(),
            name="Diffusion 图像生成",
            git_url="https://github.com/example/diffusion-gen.git",
            git_branch="main",
            git_token=None,
            created_by=admin_id,
            created_at=datetime.now() - timedelta(days=3),
        )
        session.add_all([repo1, repo2])

        # --- 数据集 ---
        dataset1 = Dataset(
            id=uuid.uuid4(),
            name="中文对话语料",
            description="精选 100 万条中文多轮对话数据",
            path="datasets/chinese-dialogue/v1.0",
            source="local",
            size_bytes=2 * 1024 * 1024 * 1024,  # 2GB
            file_count=156,
            tags=["中文", "对话", "LLM"],
            config={},
            created_by=admin_id,
            created_at=datetime.now() - timedelta(days=10),
            updated_at=datetime.now() - timedelta(days=10),
        )
        dataset2 = Dataset(
            id=uuid.uuid4(),
            name="Stable Diffusion 训练集",
            description="5 万张高质量标注图像",
            path="datasets/sd-50k/v1.0",
            source="local",
            size_bytes=50 * 1024 * 1024 * 1024,  # 50GB
            file_count=50032,
            tags=["图像", "扩散模型"],
            config={},
            created_by=admin_id,
            created_at=datetime.now() - timedelta(days=7),
            updated_at=datetime.now() - timedelta(days=7),
        )
        session.add_all([dataset1, dataset2])

        # --- 训练任务 ---
        job1 = TrainingJob(
            id=uuid.uuid4(),
            name="LLaMA3-8B 中文对话微调",
            model_config={
                "provider": "mock",
                "gpu_type": "RTX4090",
                "batch_size": 8,
                "learning_rate": 2e-5,
                "epochs": 3,
                "instance_name": "train-llm-01",
            },
            repo_url=repo1.git_url,
            repo_branch="main",
            repo_token=None,
            dataset_config={"dataset_id": str(dataset1.id)},
            training_script="train.py",
            requirements_file="requirements.txt",
            log_pattern=None,
            status="running",
            orchestrator_step="training",
            progress_info={"epoch": 2, "loss": 0.45},
            creator_id=admin_id,
            created_at=datetime.now() - timedelta(hours=2),
            started_at=datetime.now() - timedelta(hours=2),
        )
        job2 = TrainingJob(
            id=uuid.uuid4(),
            name="SD 1.5 LoRA 风格训练",
            model_config={
                "provider": "mock",
                "gpu_type": "RTX4090",
                "lora_rank": 8,
                "learning_rate": 1e-4,
                "steps": 2000,
                "instance_name": "train-sd-01",
            },
            repo_url=repo2.git_url,
            repo_branch="main",
            repo_token=None,
            dataset_config={"dataset_id": str(dataset2.id)},
            training_script="train_lora.py",
            requirements_file="requirements.txt",
            log_pattern=None,
            status="completed",
            orchestrator_step="completed",
            progress_info={"epoch": 3, "loss": 0.02},
            gpu_hours=1.5,
            total_cost=0.75,
            creator_id=admin_id,
            created_at=datetime.now() - timedelta(days=2),
            started_at=datetime.now() - timedelta(days=2),
            completed_at=datetime.now() - timedelta(days=1, hours=20),
        )
        job3 = TrainingJob(
            id=uuid.uuid4(),
            name="分类模型基线训练",
            model_config={
                "provider": "mock",
                "gpu_type": "RTX3090",
                "model": "bert-base",
            },
            repo_url="https://github.com/example/text-classify.git",
            repo_branch="main",
            repo_token=None,
            dataset_config={},
            training_script="train.py",
            requirements_file="requirements.txt",
            log_pattern=None,
            status="failed",
            orchestrator_step="setup_env",
            progress_info={"step": 2},
            error_message="requirements.txt 依赖安装失败",
            creator_id=admin_id,
            created_at=datetime.now() - timedelta(days=5),
            started_at=datetime.now() - timedelta(days=5),
            completed_at=datetime.now() - timedelta(days=5, hours=1),
        )
        session.add_all([job1, job2, job3])

        # --- 训练步骤 ---
        step1 = TrainingTaskStep(
            id=uuid.uuid4(),
            job_id=job1.id,
            step_name="pulling_code",
            status="completed",
            started_at=datetime.now() - timedelta(hours=2),
            completed_at=datetime.now() - timedelta(hours=1, minutes=50),
        )
        step2 = TrainingTaskStep(
            id=uuid.uuid4(),
            job_id=job1.id,
            step_name="setup_env",
            status="completed",
            started_at=datetime.now() - timedelta(hours=1, minutes=45),
            completed_at=datetime.now() - timedelta(hours=1, minutes=20),
        )
        step3 = TrainingTaskStep(
            id=uuid.uuid4(),
            job_id=job1.id,
            step_name="training",
            status="running",
            started_at=datetime.now() - timedelta(hours=1),
        )
        session.add_all([step1, step2, step3])

        # --- 制品 ---
        artifact1 = Artifact(
            id=uuid.uuid4(),
            job_id=job2.id,
            name="pytorch_model.bin",
            path=f"artifacts/{job2.id}/pytorch_model.bin",
            artifact_type="checkpoint",
            size_bytes=4 * 1024 * 1024 * 1024,  # 4GB
            storage_location="minio",
            created_at=datetime.now() - timedelta(days=1, hours=20),
        )
        artifact2 = Artifact(
            id=uuid.uuid4(),
            job_id=job2.id,
            name="training.log",
            path=f"artifacts/{job2.id}/training.log",
            artifact_type="log",
            size_bytes=15 * 1024 * 1024,  # 15MB
            storage_location="minio",
            created_at=datetime.now() - timedelta(days=1, hours=20),
        )
        session.add_all([artifact1, artifact2])

        await session.commit()

    print("OK")
    print("   - Repos: 2")
    print("   - Datasets: 2")
    print("   - Jobs: 3 (running x1, success x1, failed x1)")
    print("   - Steps: 3")
    print("   - Artifacts: 2")


if __name__ == "__main__":
    asyncio.run(seed_cloud_data())
