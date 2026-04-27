"""Blog routes integration tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.tests.conftest import patch_container_service


@pytest.fixture
def blog_service_mock(db_container):
    service = MagicMock()
    service.list_posts = AsyncMock(return_value={"items": [], "total": 0})
    service.create_post = AsyncMock(return_value={"id": str(uuid.uuid4())})
    service.list_my_posts = AsyncMock(return_value={"items": [], "total": 0})
    service.list_pending_posts = AsyncMock(return_value={"items": [], "total": 0})
    service.approve_post = AsyncMock(return_value={"status": "published"})
    service.reject_post = AsyncMock(return_value={"status": "rejected"})
    service.check_favorite = AsyncMock(return_value=True)
    service.create_report = AsyncMock(return_value={"id": str(uuid.uuid4())})
    return patch_container_service(db_container, "blog", service)


@pytest.mark.asyncio
class TestBlogAPI:
    async def test_public_posts_list_uses_guest_level(self, client, blog_service_mock):
        response = await client.get(
            "/api/blog/posts",
            params={"page": 2, "page_size": 5, "sort_by": "created_at", "q": "python"},
        )
        assert response.status_code == 200
        assert response.json()["code"] == "ok"
        blog_service_mock.list_posts.assert_awaited_once_with(
            page=2,
            page_size=5,
            status_filter="published",
            sort_by="created_at",
            user_level=5,
            search_query="python",
            tag_filter=None,
        )

    async def test_create_post_requires_auth(self, client):
        payload = {"title": "t", "content": "c", "tags": [], "access_level": "A5"}
        response = await client.post("/api/blog/posts", json=payload)
        assert response.status_code == 401

    async def test_my_posts_and_create_report_with_auth(
        self, client, auth_headers, blog_service_mock
    ):
        mine = await client.get("/api/blog/my-posts", headers=auth_headers)
        assert mine.status_code == 200
        assert mine.json()["code"] == "ok"

        report = await client.post(
            "/api/blog/reports",
            json={"post_id": str(uuid.uuid4()), "reason": "spam"},
            headers=auth_headers,
        )
        assert report.status_code == 200
        assert report.json()["code"] == "ok"
        blog_service_mock.create_report.assert_awaited_once()

    async def test_moderation_requires_admin(self, client, auth_headers):
        denied = await client.get("/api/blog/moderation/pending", headers=auth_headers)
        assert denied.status_code == 403

    async def test_admin_can_list_and_approve_moderation(
        self, client, admin_headers, blog_service_mock
    ):
        pending = await client.get("/api/blog/moderation/pending", headers=admin_headers)
        assert pending.status_code == 200
        assert pending.json()["code"] == "ok"
        blog_service_mock.list_pending_posts.assert_awaited_once()

        approved = await client.post(
            f"/api/blog/moderation/{uuid.uuid4()}/approve",
            headers=admin_headers,
        )
        assert approved.status_code == 200
        assert approved.json()["code"] == "ok"
        blog_service_mock.approve_post.assert_awaited_once()

    async def test_favorite_status_for_guest_returns_false(self, client):
        response = await client.get(f"/api/blog/posts/{uuid.uuid4()}/favorite-status")
        assert response.status_code == 200
        assert response.json()["data"]["favorited"] is False
