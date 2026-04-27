"""Asset management service tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from backend.plugins.asset_mgmt.services import AssetMgmtService
from backend.plugins.blog.models import BlogPost
from backend.plugins.cloud_integration.models import TrainingJob
from backend.plugins.crawler.models import CrawlRecord
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
                    content="notes about training and deployment",
                    created_at=now,
                ),
                BlogPost(
                    author_id=other_owner_id,
                    title="Other Notes",
                    slug="other-notes",
                    content="not visible to owner",
                    created_at=now,
                ),
                OSSFile(
                    owner_id=owner_id,
                    path="uploads/report.pdf",
                    size=128,
                    mime_type="application/pdf",
                    created_at=now,
                ),
                CrawlRecord(
                    url="https://example.com/model",
                    title="Crawler Model Page",
                    content_type="article",
                    status_code=200,
                    source="example.com",
                    crawled_at=now,
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

    return owner_id


@pytest.mark.asyncio
class TestAssetMgmtService:
    async def test_list_assets_aggregates_supported_sources(
        self, db_container, asset_seed_data
    ):
        service = AssetMgmtService(db_container)

        result = await service.list_assets(
            owner_id=asset_seed_data,
            page=1,
            page_size=10,
        )

        types = {item["asset_type"] for item in result["items"]}
        assert result["total"] == 4
        assert types == {"blog_post", "file", "crawl_result", "training_job"}
        assert "Other Notes" not in {item["title"] for item in result["items"]}

    async def test_list_assets_filter_pagination_and_search(
        self, db_container, asset_seed_data
    ):
        service = AssetMgmtService(db_container)

        files = await service.list_assets(
            owner_id=asset_seed_data,
            asset_type="file",
            page=1,
            page_size=1,
        )
        assert files["total"] == 1
        assert files["items"][0]["title"] == "report.pdf"

        results = await service.search_assets(
            owner_id=asset_seed_data,
            keyword="model",
            date_from="2000-01-01T00:00:00",
            date_to="2999-01-01T00:00:00",
        )
        assert {item["asset_type"] for item in results} == {
            "blog_post",
            "crawl_result",
            "training_job",
        }

    async def test_get_stats_counts_assets_by_type(self, db_container, asset_seed_data):
        service = AssetMgmtService(db_container)

        stats = await service.get_stats(owner_id=asset_seed_data)

        assert stats["by_type"]["blog_post"] == 1
        assert stats["by_type"]["file"]["count"] == 1
        assert stats["by_type"]["file"]["total_size_bytes"] == 128
        assert stats["by_type"]["crawl_result"] == 1
        assert stats["by_type"]["training_job"] == 1
        assert stats["total_assets"] == 4
