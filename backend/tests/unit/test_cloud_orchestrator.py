"""TrainingOrchestrator 单元测试。"""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.plugins.cloud_integration.orchestrator import Step, TrainingOrchestrator


@pytest.mark.asyncio
class TestTrainingOrchestrator:
    async def test_process_job_dispatch(self):
        orch = TrainingOrchestrator(MagicMock())
        orch._step_create_instance = AsyncMock()
        job = SimpleNamespace(id=uuid.uuid4(), orchestrator_step=Step.CREATING_INSTANCE)
        await orch._process_job(job)
        orch._step_create_instance.assert_awaited_once()

    async def test_process_idle_advances(self):
        orch = TrainingOrchestrator(MagicMock())
        orch._advance_step = AsyncMock()
        job = SimpleNamespace(id=uuid.uuid4(), orchestrator_step=Step.IDLE)
        await orch._process_job(job)
        orch._advance_step.assert_awaited_once()

    async def test_step_create_instance_success(self):
        orch = TrainingOrchestrator(MagicMock())
        orch._begin_step = AsyncMock()
        orch._complete_step = AsyncMock()
        orch._advance_step = AsyncMock()
        orch._fail_job = AsyncMock()
        service = MagicMock()
        service.create_instance = AsyncMock(return_value={"id": "inst-1"})
        orch._get_service = MagicMock(return_value=service)
        job = SimpleNamespace(
            id=uuid.uuid4(),
            name="job",
            model_config={"gpu_type": "RTX4090", "provider": "mock"},
        )
        await orch._step_create_instance(job)
        orch._complete_step.assert_awaited_once()
        orch._advance_step.assert_awaited_once_with(job.id, Step.WAITING_INSTANCE)
        orch._fail_job.assert_not_called()

    async def test_step_create_instance_failure(self):
        orch = TrainingOrchestrator(MagicMock())
        orch._begin_step = AsyncMock()
        orch._fail_job = AsyncMock()
        service = MagicMock()
        service.create_instance = AsyncMock(side_effect=RuntimeError("x"))
        orch._get_service = MagicMock(return_value=service)
        job = SimpleNamespace(id=uuid.uuid4(), name="job", model_config={})
        await orch._step_create_instance(job)
        orch._fail_job.assert_awaited_once()

    async def test_step_connect_ssh_retry_when_no_host(self):
        session = AsyncMock()
        session.execute = AsyncMock(
            return_value=SimpleNamespace(scalar_one_or_none=lambda: None)
        )

        class _SessionCtx:
            async def __aenter__(self):
                return session

            async def __aexit__(self, exc_type, exc, tb):
                return False

        def _session_factory():
            return _SessionCtx()

        container = MagicMock()
        container.get = lambda name: {"session_factory": _session_factory} if name == "db" else MagicMock()
        orch = TrainingOrchestrator(container)
        orch._begin_step = AsyncMock()
        orch._retry_step = AsyncMock()
        job = SimpleNamespace(id=uuid.uuid4())
        await orch._step_connect_ssh(job)
        orch._retry_step.assert_awaited_once()

    async def test_retry_step_fail_when_exhausted(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=SimpleNamespace(fetchone=lambda: [1]))

        class _SessionCtx:
            async def __aenter__(self):
                return session

            async def __aexit__(self, exc_type, exc, tb):
                return False

        def _session_factory():
            return _SessionCtx()

        container = MagicMock()
        container.get = lambda name: {"session_factory": _session_factory} if name == "db" else MagicMock()
        orch = TrainingOrchestrator(container)
        orch.MAX_RETRY = 1
        orch._fail_job = AsyncMock()
        job = SimpleNamespace(id=uuid.uuid4())
        await orch._retry_step(job, Step.CONNECTING_SSH, "err")
        orch._fail_job.assert_awaited_once()
