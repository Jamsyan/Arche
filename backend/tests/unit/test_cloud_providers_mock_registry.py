"""mock provider 与 registry 单元测试。"""

from __future__ import annotations

import pytest

from backend.plugins.cloud_integration.providers import registry
from backend.plugins.cloud_integration.providers.base import CloudProvider
from backend.plugins.cloud_integration.providers.mock import MockProvider


class _DummyProvider(CloudProvider):
    name = "dummy"

    async def create_instance(self, job_id: str, config: dict) -> dict:
        return {}

    async def start_instance(self, instance_id: str) -> dict:
        return {}

    async def stop_instance(self, instance_id: str) -> dict:
        return {}

    async def delete_instance(self, instance_id: str) -> None:
        return None

    async def get_instance_status(self, instance_id: str) -> dict:
        return {}

    async def get_gpu_metrics(self, instance_id: str) -> dict:
        return {}

    async def get_cost(self, instance_id: str, start: str, end: str) -> float:
        return 0.0


@pytest.fixture
def restore_provider_registry():
    """快照/还原模块级 _providers，避免 `dummy` 等测试用注册污染其他用例。"""
    snapshot = dict(registry._providers)
    try:
        yield
    finally:
        registry._providers.clear()
        registry._providers.update(snapshot)


class TestRegistry:
    def test_register_and_get_provider(self, restore_provider_registry):
        registry.register("dummy", _DummyProvider)
        provider = registry.get_provider("dummy", {"a": 1})
        assert isinstance(provider, _DummyProvider)

    def test_get_provider_unknown_raises(self):
        with pytest.raises(ValueError):
            registry.get_provider("not_exists")


@pytest.mark.asyncio
class TestMockProvider:
    async def test_lifecycle_and_metrics(self):
        provider = MockProvider({})
        inst = await provider.create_instance("job1", {"gpu_type": "A100", "gpu_count": 1})
        assert inst["status"] == "pending"
        iid = inst["instance_id"]

        started = await provider.start_instance(iid)
        assert started["status"] == "running"
        metrics = await provider.get_gpu_metrics(iid)
        assert "utilization_pct" in metrics
        stopped = await provider.stop_instance(iid)
        assert stopped["status"] == "stopped"
        cost = await provider.get_cost(iid, "", "")
        assert cost >= 0

    async def test_missing_instance_raises_or_zero(self):
        provider = MockProvider({})
        with pytest.raises(RuntimeError):
            await provider.start_instance("none")
        assert await provider.get_cost("none", "", "") == 0.0
