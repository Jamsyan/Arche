"""CloudTrainingService 主流程单元测试。"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from backend.core.middleware import AppError
from backend.plugins.cloud_integration.models import TrainingInstance
from backend.plugins.cloud_integration.services import CloudTrainingService


@pytest.mark.asyncio
class TestCloudServicesWorkflow:
    async def test_transition_validation(self, db_container):
        service = CloudTrainingService(db_container)
        service._transition("pending", "running")
        with pytest.raises(AppError):
            service._transition("completed", "running")

    async def test_create_and_launch_job(self, db_container):
        service = CloudTrainingService(db_container)
        creator = uuid.uuid4()
        job = await service.create_job(
            creator_id=creator,
            name="j1",
            model_config={},
            repo_url="https://github.com/a/b.git",
        )
        assert job["status"] == "pending"
        launched = await service.launch_job(uuid.UUID(job["id"]))
        assert launched["orchestrator_step"] == "creating_instance"

    async def test_create_job_missing_repo(self, db_container):
        service = CloudTrainingService(db_container)
        with pytest.raises(AppError) as exc:
            await service.create_job(
                creator_id=uuid.uuid4(),
                name="j1",
                model_config={},
                repo_url=None,
            )
        assert exc.value.code == "missing_repo"

    async def test_start_stop_complete_fail_job(self, db_container):
        service = CloudTrainingService(db_container)
        job = await service.create_job(
            creator_id=uuid.uuid4(),
            name="j2",
            model_config={},
            repo_url="https://github.com/a/b.git",
        )
        jid = uuid.UUID(job["id"])
        started = await service.start_job(jid)
        assert started["status"] == "running"
        failed = await service.fail_job(jid, "err")
        assert failed["status"] == "failed"

    async def test_create_start_stop_instance_and_cost(self, db_container, monkeypatch):
        service = CloudTrainingService(db_container)
        job = await service.create_job(
            creator_id=uuid.uuid4(),
            name="j3",
            model_config={},
            repo_url="https://github.com/a/b.git",
        )
        jid = uuid.UUID(job["id"])

        provider = AsyncMock()
        provider.create_instance = AsyncMock(
            return_value={
                "instance_id": "pi-1",
                "gpu_count": 1,
                "host": "1.1.1.1",
                "port": 22,
                "user": "root",
            }
        )
        provider.start_instance = AsyncMock()
        provider.stop_instance = AsyncMock()
        service._provider = provider

        inst = await service.create_instance(jid, "ins", "RTX4090", provider="mock")
        iid = uuid.UUID(inst["id"])
        await service.start_instance(iid)

        # 修正 started_at，避免费用为 0
        async with service.session_factory() as session:
            r = await session.get(TrainingInstance, iid)
            r.started_at = datetime.now(timezone.utc) - timedelta(hours=1)
            await session.commit()

        monkeypatch.setattr(
            "backend.plugins.cloud_integration.cost.calculator.calculate_instance_cost",
            lambda *args, **kwargs: 8.8,
        )
        monkeypatch.setattr(
            "backend.plugins.cloud_integration.cost.calculator.calculate_rate",
            lambda *args, **kwargs: 8.8,
        )

        class _FakeDateTime:
            @staticmethod
            def now(_tz=None):
                return datetime.now()

        monkeypatch.setattr(
            "backend.plugins.cloud_integration.services.datetime",
            _FakeDateTime,
        )
        stopped = await service.stop_instance(iid)
        assert stopped["status"] == "stopped"

    async def test_provider_error_wrapped(self, db_container):
        service = CloudTrainingService(db_container)
        job = await service.create_job(
            creator_id=uuid.uuid4(),
            name="j4",
            model_config={},
            repo_url="https://github.com/a/b.git",
        )
        service._provider = AsyncMock()
        service._provider.create_instance = AsyncMock(side_effect=RuntimeError("boom"))
        with pytest.raises(AppError) as exc:
            await service.create_instance(uuid.UUID(job["id"]), "x", "RTX4090")
        assert exc.value.code == "provider_error"

    async def test_list_and_delete_job(self, db_container):
        service = CloudTrainingService(db_container)
        creator = uuid.uuid4()
        job = await service.create_job(
            creator_id=creator,
            name="j5",
            model_config={},
            repo_url="https://github.com/a/b.git",
        )
        listed = await service.list_jobs(creator_id=creator)
        assert listed["total"] >= 1
        await service.delete_job(uuid.UUID(job["id"]))
        with pytest.raises(AppError):
            await service.get_job(uuid.UUID(job["id"]))
