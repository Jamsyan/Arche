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
    service.get_job = AsyncMock(return_value={"id": str(uuid.uuid4()), "name": "j"})
    service.create_job = AsyncMock(return_value={"id": str(uuid.uuid4()), "name": "j"})
    service.delete_job = AsyncMock(return_value=None)
    service.start_job = AsyncMock(return_value={"status": "running"})
    service.stop_job = AsyncMock(return_value={"status": "stopped"})
    service.complete_job = AsyncMock(return_value={"status": "completed"})
    service.fail_job = AsyncMock(return_value={"status": "failed"})
    service.get_job_logs = AsyncMock(return_value={"lines": ["ok"]})
    service.list_instances = AsyncMock(return_value={"items": [], "total": 0})
    service.create_instance = AsyncMock(return_value={"id": str(uuid.uuid4())})
    service.start_instance = AsyncMock(return_value={"status": "running"})
    service.stop_instance = AsyncMock(return_value={"status": "stopped"})
    service.launch_job = AsyncMock(
        return_value={"id": str(uuid.uuid4()), "orchestrator_step": "creating_instance"}
    )
    service.get_job_progress = AsyncMock(return_value={"progress": 50})
    service.get_job_steps = AsyncMock(return_value={"items": []})
    service.get_costs = AsyncMock(return_value={"total_cost": 0, "breakdown": []})
    service.list_datasets = AsyncMock(return_value={"items": [], "total": 0})
    service.create_dataset = AsyncMock(
        return_value={"id": str(uuid.uuid4()), "name": "ds"}
    )
    service.get_dataset = AsyncMock(
        return_value={"id": str(uuid.uuid4()), "name": "ds"}
    )
    service.delete_dataset = AsyncMock(return_value=None)
    service.sync_dataset = AsyncMock(return_value={"status": "queued"})
    service.list_repos = AsyncMock(return_value={"items": [], "total": 0})
    service.create_repo = AsyncMock(
        return_value={"id": str(uuid.uuid4()), "name": "repo"}
    )
    service.delete_repo = AsyncMock(return_value=None)
    service.sync_repo = AsyncMock(return_value={"status": "queued"})
    service.list_artifacts = AsyncMock(return_value={"items": [], "total": 0})
    service.get_artifact = AsyncMock(
        return_value={"id": str(uuid.uuid4()), "name": "ckpt"}
    )
    service.download_artifact = AsyncMock(return_value="https://download.local/ckpt")
    service.delete_artifact = AsyncMock(return_value=None)
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

    async def test_create_and_launch_job(
        self, client, admin_headers, cloud_service_mock
    ):
        payload = {
            "name": "job",
            "config": {},
            "repo_url": "https://github.com/a/b.git",
            "repo_branch": "main",
            "provider": "mock",
            "gpu_type": "RTX4090",
        }
        created = await client.post(
            "/api/cloud/jobs", headers=admin_headers, json=payload
        )
        assert created.status_code == 200
        assert created.json()["code"] == "ok"

        job_id = str(uuid.uuid4())
        launched = await client.post(
            f"/api/cloud/jobs/{job_id}/launch", headers=admin_headers
        )
        assert launched.status_code == 200
        assert launched.json()["code"] == "ok"

    async def test_job_detail_actions_logs_and_instances(
        self, client, admin_headers, cloud_service_mock
    ):
        job_id = str(uuid.uuid4())
        instance_id = str(uuid.uuid4())

        paths = [
            ("get", f"/api/cloud/jobs/{job_id}", None),
            ("post", f"/api/cloud/jobs/{job_id}/start", None),
            ("post", f"/api/cloud/jobs/{job_id}/stop", None),
            ("post", f"/api/cloud/jobs/{job_id}/complete", {"result_path": "runs/out"}),
            ("post", f"/api/cloud/jobs/{job_id}/fail", {"error_message": "boom"}),
            ("get", f"/api/cloud/jobs/{job_id}/logs", {"lines": 10}),
            ("get", f"/api/cloud/jobs/{job_id}/instances", None),
            ("post", f"/api/cloud/instances/{instance_id}/start", None),
            ("post", f"/api/cloud/instances/{instance_id}/stop", None),
            ("get", f"/api/cloud/jobs/{job_id}/progress", None),
            ("get", f"/api/cloud/jobs/{job_id}/steps", None),
            ("delete", f"/api/cloud/jobs/{job_id}", None),
        ]

        for method, path, params in paths:
            response = await getattr(client, method)(
                path,
                params=params,
                headers=admin_headers,
            )
            assert response.status_code == 200
            assert response.json()["code"] == "ok"

        created_instance = await client.post(
            f"/api/cloud/jobs/{job_id}/instances",
            headers=admin_headers,
            json={"instance_name": "gpu-1", "gpu_type": "RTX4090", "provider": "mock"},
        )
        assert created_instance.status_code == 200
        cloud_service_mock.create_instance.assert_awaited_once()

    async def test_dataset_repo_and_artifact_routes(
        self, client, admin_headers, cloud_service_mock
    ):
        dataset_id = str(uuid.uuid4())
        repo_id = str(uuid.uuid4())
        artifact_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())

        dataset_payload = {
            "name": "dataset",
            "description": "sample",
            "path": "datasets/sample",
            "source": "local",
            "tags": ["demo"],
            "config": {},
        }
        repo_payload = {
            "name": "repo",
            "git_url": "https://github.com/a/b.git",
            "git_branch": "main",
        }

        requests = [
            ("get", "/api/cloud/stats", None, None),
            ("get", "/api/cloud/datasets", {"source": "local"}, None),
            ("post", "/api/cloud/datasets", None, dataset_payload),
            ("get", f"/api/cloud/datasets/{dataset_id}", None, None),
            ("post", f"/api/cloud/datasets/{dataset_id}/sync", None, None),
            ("delete", f"/api/cloud/datasets/{dataset_id}", None, None),
            ("get", "/api/cloud/repos", None, None),
            ("post", "/api/cloud/repos", None, repo_payload),
            ("post", f"/api/cloud/repos/{repo_id}/sync", None, None),
            ("delete", f"/api/cloud/repos/{repo_id}", None, None),
            (
                "get",
                "/api/cloud/artifacts",
                {"job_id": job_id, "artifact_type": "log"},
                None,
            ),
            ("get", f"/api/cloud/artifacts/{artifact_id}", None, None),
            ("get", f"/api/cloud/artifacts/{artifact_id}/download", None, None),
            ("delete", f"/api/cloud/artifacts/{artifact_id}", None, None),
        ]

        for method, path, params, json in requests:
            response = await client.request(
                method.upper(),
                path,
                params=params,
                json=json,
                headers=admin_headers,
            )
            assert response.status_code == 200
            assert response.json()["code"] == "ok"
