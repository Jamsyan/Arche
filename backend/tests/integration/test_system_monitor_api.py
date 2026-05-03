"""system_monitor routes integration smoke tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from backend.tests.conftest import patch_container_service


@pytest.fixture
def system_monitor_mock(db_container):
    service = MagicMock()
    service.get_summary.return_value = {"cpu_percent": 12.5}
    service.get_cpu_detail.return_value = {"count_logical": 8}
    service.get_memory_detail.return_value = {"percent": 40.0}
    service.get_disk_detail.return_value = {"root_percent": 50.0, "partitions": []}
    service.get_network_io.return_value = {"bytes_sent": 10, "bytes_recv": 20}
    service.get_history.return_value = {"items": [], "total": 0, "page": 2}
    service.get_processes.return_value = {"items": [], "total": 0, "limit": 5}
    return patch_container_service(db_container, "system_monitor", service)


@pytest.mark.asyncio
class TestSystemMonitorAPI:
    async def test_system_monitor_requires_auth(self, client):
        response = await client.get("/api/system/summary")
        assert response.status_code == 401

    async def test_system_monitor_summary_and_details(
        self, client, admin_headers, system_monitor_mock
    ):
        endpoints = [
            ("/api/system/summary", "cpu_percent"),
            ("/api/system/cpu", "count_logical"),
            ("/api/system/memory", "percent"),
            ("/api/system/disk", "partitions"),
            ("/api/system/network", "bytes_sent"),
        ]

        for path, expected_key in endpoints:
            response = await client.get(path, headers=admin_headers)
            assert response.status_code == 200
            assert response.json()["code"] == "ok"
            assert expected_key in response.json()["data"]

    async def test_system_monitor_history_and_processes(
        self, client, admin_headers, system_monitor_mock
    ):
        history = await client.get(
            "/api/system/history",
            params={"page": 2, "page_size": 10},
            headers=admin_headers,
        )
        assert history.status_code == 200
        system_monitor_mock.get_history.assert_called_once_with(page=2, page_size=10)

        processes = await client.get(
            "/api/system/processes",
            params={"sort_by": "pid", "limit": 5},
            headers=admin_headers,
        )
        assert processes.status_code == 200
        system_monitor_mock.get_processes.assert_called_once_with(
            sort_by="pid", limit=5
        )
