"""cloud routes 最小烟囱集成测试。"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.tests.conftest import patch_container_service


@pytest.fixture
def cloud_service_mock(db_container):
    service = MagicMock()
    service.list_jobs = AsyncMock(return_value={"items": [], "total": 0})
    service.create_job = AsyncMock(return_value={"id": str(uuid.uuid4()), "name": "j"})
    service.launch_job = AsyncMock(return_value={"id": str(uuid.uuid4()), "orchestrator_step": "creating_instance"})
    service.get_costs = AsyncMock(return_value={"total_cost": 0, "breakdown": []})
    return patch_container_service(db_container, "cloud_training", service)


@pytest.mark.asyncio
class TestCloudRoutesAPI:
    async def test_list_jobs_requires_auth(self, client):
        res = await client.get("/api/cloud/jobs")
        assert res.status_code == 401

    async def test_list_jobs_and_costs(self, client, admin_headers, cloud_service_mock):
        res = await client.get("/api/cloud/jobs", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["code"] == "ok"
        cloud_service_mock.list_jobs.assert_awaited_once()

        costs = await client.get("/api/cloud/costs", headers=admin_headers)
        assert costs.status_code == 200
        assert costs.json()["code"] == "ok"

    async def test_create_and_launch_job(self, client, admin_headers, cloud_service_mock):
        payload = {
            "name": "job",
            "config": {},
            "repo_url": "https://github.com/a/b.git",
            "repo_branch": "main",
            "provider": "mock",
            "gpu_type": "RTX4090",
        }
        created = await client.post("/api/cloud/jobs", headers=admin_headers, json=payload)
        assert created.status_code == 200
        assert created.json()["code"] == "ok"

        job_id = str(uuid.uuid4())
        launched = await client.post(f"/api/cloud/jobs/{job_id}/launch", headers=admin_headers)
        assert launched.status_code == 200
        assert launched.json()["code"] == "ok"
