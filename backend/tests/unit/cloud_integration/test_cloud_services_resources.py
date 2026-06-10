"""CloudTrainingService 资源管理单元测试。"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.core.middleware import AppError
from backend.plugins.cloud_integration.models import Artifact, TrainingJob
from backend.plugins.cloud_integration.services import CloudTrainingService
from backend.tests.conftest import patch_container_service


@pytest.fixture
def storage_mock(db_container):
    """注入 storage 服务 mock，返回 (storage, unified) 二元组。

    多个资源删除测试都需要校验底层 unified storage 的 delete 调用，
    用同一组 AsyncMock 收敛到 fixture，避免重复样板。
    """
    storage = AsyncMock()
    unified = AsyncMock()
    storage.get_unified_storage = MagicMock(return_value=unified)
    patch_container_service(db_container, "storage", storage)
    return storage, unified


@pytest.mark.asyncio
class TestCloudServicesResources:
    async def test_dataset_crud_and_duplicate_path(self, db_container):
        service = CloudTrainingService(db_container)
        creator = uuid.uuid4()
        dataset = await service.create_dataset(
            creator_id=creator,
            name="d1",
            description=None,
            path="datasets/a",
            source="local",
            tags=["x"],
            config={},
        )
        assert dataset["path"] == "datasets/a"
        got = await service.get_dataset(uuid.UUID(dataset["id"]))
        assert got["name"] == "d1"
        listed = await service.list_datasets(creator_id=creator)
        assert listed["total"] == 1
        with pytest.raises(AppError):
            await service.create_dataset(
                creator_id=creator,
                name="d2",
                description=None,
                path="datasets/a",
                source="local",
                tags=[],
                config={},
            )

    async def test_delete_dataset_and_artifact_calls_storage(
        self, db_container, storage_mock
    ):
        _storage, unified = storage_mock
        service = CloudTrainingService(db_container)
        creator = uuid.uuid4()
        ds = await service.create_dataset(
            creator_id=creator,
            name="d1",
            description=None,
            path="datasets/x",
            source="local",
            tags=[],
            config={},
        )

        await service.delete_dataset(uuid.UUID(ds["id"]))
        unified.delete.assert_awaited()

    async def test_repo_crud_and_duplicate_url(self, db_container):
        service = CloudTrainingService(db_container)
        creator = uuid.uuid4()
        repo = await service.create_repo(
            creator_id=creator,
            name="r1",
            git_url="https://github.com/a/b.git",
            git_branch="main",
            git_token=None,
        )
        assert repo["git_url"].endswith("b.git")
        listed = await service.list_repos(creator_id=creator)
        assert listed["total"] == 1
        with pytest.raises(AppError):
            await service.create_repo(
                creator_id=creator,
                name="r2",
                git_url="https://github.com/a/b.git",
                git_branch="main",
                git_token=None,
            )
        await service.delete_repo(uuid.UUID(repo["id"]))

    async def test_artifact_list_get_download_delete(self, db_container, storage_mock):
        _storage, unified = storage_mock
        service = CloudTrainingService(db_container)
        creator = uuid.uuid4()
        async with service.session_factory() as session:
            job = TrainingJob(
                creator_id=creator,
                name="j",
                model_config={},
                status="pending",
                repo_url="https://github.com/a/b.git",
            )
            session.add(job)
            await session.flush()
            art = Artifact(
                job_id=job.id,
                name="a.bin",
                path="out/a.bin",
                artifact_type="checkpoint",
            )
            session.add(art)
            await session.commit()
            aid = art.id

        listed = await service.list_artifacts(creator_id=creator)
        assert listed["total"] == 1
        one = await service.get_artifact(aid)
        assert one["name"] == "a.bin"
        url = await service.download_artifact(aid)
        assert url.endswith("out/a.bin")

        await service.delete_artifact(aid)
        unified.delete.assert_awaited()
