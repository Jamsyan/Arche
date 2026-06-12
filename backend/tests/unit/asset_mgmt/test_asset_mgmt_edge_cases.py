"""资产管理边缘用例测试。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from backend.plugins.asset_mgmt.services import AssetMgmtService
from backend.plugins.blog.models import BlogPost
from backend.plugins.cloud_integration.models import TrainingJob
from backend.plugins.oss.models import OSSFile


@pytest.fixture
async def asset_seed_data(db_container):
    owner_id = uuid.uuid4()
    other_owner_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    async with db_container.get("db")["session_factory"]() as session:
        session.add_all(
            [
                BlogPost(
                    author_id=owner_id,
                    title="Model Notes",
                    slug="model-notes",
                    created_at=now,
                ),
                BlogPost(
                    author_id=other_owner_id,
                    title="Other Notes",
                    slug="other-notes",
                    created_at=now,
                ),
                OSSFile(
                    owner_id=owner_id,
                    path="uploads/report.pdf",
                    size=128,
                    mime_type="application/pdf",
                    created_at=now,
                ),
                TrainingJob(
                    creator_id=owner_id,
                    name="Train model",
                    model_config={"lr": 0.1},
                    status="running",
                    created_at=now,
                ),
            ]
        )
        await session.commit()

    return owner_id, other_owner_id


@pytest.mark.asyncio
class TestAssetMgmtEdgeCases:
    """资产管理边缘用例：空状态、分页边界、搜索过滤、权限边界。"""

    # ── 空状态 ──

    async def test_list_assets_empty_user(self, db_container):
        empty_owner = uuid.uuid4()
        service = AssetMgmtService(db_container)

        result = await service.list_assets(owner_id=empty_owner, page=1, page_size=10)

        assert result["items"] == []
        assert result["total"] == 0
        assert result["page"] == 1
        assert result["page_size"] == 10

    async def test_search_assets_no_match(self, db_container, asset_seed_data):
        owner_id, _ = asset_seed_data
        service = AssetMgmtService(db_container)

        results = await service.search_assets(
            owner_id=owner_id, keyword="nonexistent_keyword_xyz"
        )

        assert results == []

    async def test_get_stats_empty_user(self, db_container):
        empty_owner = uuid.uuid4()
        service = AssetMgmtService(db_container)

        stats = await service.get_stats(owner_id=empty_owner)

        assert stats["by_type"]["blog_post"] == 0
        assert stats["by_type"]["file"]["count"] == 0
        assert stats["by_type"]["file"]["total_size_bytes"] == 0
        assert stats["by_type"]["crawl_result"] == 0
        assert stats["by_type"]["training_job"] == 0
        assert stats["total_assets"] == 0
        assert stats["total"] == 0

    # ── 分页边界值 ──

    async def test_pagination_page_beyond_total(self, db_container, asset_seed_data):
        owner_id, _ = asset_seed_data
        service = AssetMgmtService(db_container)

        result = await service.list_assets(owner_id=owner_id, page=999, page_size=10)

        assert result["items"] == []
        assert result["total"] == 3
        assert result["page"] == 999

    async def test_pagination_large_page_size(self, db_container, asset_seed_data):
        owner_id, _ = asset_seed_data
        service = AssetMgmtService(db_container)

        result = await service.list_assets(owner_id=owner_id, page=1, page_size=9999)

        assert len(result["items"]) == 3
        assert result["total"] == 3

    async def test_pagination_negative_page_gets_default(
        self, db_container, asset_seed_data
    ):
        owner_id, _ = asset_seed_data
        service = AssetMgmtService(db_container)

        result = await service.list_assets(owner_id=owner_id, page=0, page_size=10)

        assert result["items"] == []
        assert result["total"] == 3

    # ── 搜索过滤 ──

    async def test_search_with_date_range(self, db_container, asset_seed_data):
        owner_id, _ = asset_seed_data
        service = AssetMgmtService(db_container)

        results = await service.search_assets(
            owner_id=owner_id,
            keyword="model",
            date_from="2099-01-01T00:00:00",
            date_to="3099-01-01T00:00:00",
        )

        assert results == []

        results = await service.search_assets(
            owner_id=owner_id,
            keyword="model",
            date_from="2000-01-01T00:00:00",
            date_to="2099-01-01T00:00:00",
        )

        assert len(results) >= 1

    async def test_search_with_asset_type(self, db_container, asset_seed_data):
        owner_id, _ = asset_seed_data
        service = AssetMgmtService(db_container)

        results = await service.search_assets(
            owner_id=owner_id,
            keyword="model",
            asset_type="training_job",
        )

        assert len(results) == 1
        assert results[0]["asset_type"] == "training_job"

    # ── 权限边界 ──

    async def test_other_owner_assets_not_visible(self, db_container, asset_seed_data):
        owner_id, other_owner_id = asset_seed_data
        service = AssetMgmtService(db_container)

        owner_result = await service.list_assets(
            owner_id=owner_id, page=1, page_size=10
        )
        owner_titles = {item["title"] for item in owner_result["items"]}
        assert "Other Notes" not in owner_titles

        other_result = await service.list_assets(
            owner_id=other_owner_id, page=1, page_size=10
        )
        other_titles = {item["title"] for item in other_result["items"]}
        assert "Other Notes" in other_titles
        assert "Model Notes" not in other_titles
        assert "report.pdf" not in other_titles
