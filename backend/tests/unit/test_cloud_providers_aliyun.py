"""Aliyun provider 单元测试。"""

from __future__ import annotations

import pytest

from backend.core.middleware import AppError
from backend.plugins.cloud_integration.providers.aliyun import AliyunProvider


@pytest.mark.asyncio
class TestAliyunProvider:
    async def test_missing_core_config_raises(self):
        provider = AliyunProvider(
            {
                "access_key_id": "a",
                "access_key_secret": "b",
                # 缺 security_group_id / vswitch_id / image_id
            }
        )
        with pytest.raises(AppError) as exc:
            await provider.create_instance("job", {})
        assert exc.value.code == "aliyun_config_missing"

    async def test_start_stop_and_cost_fallback(self, monkeypatch):
        provider = AliyunProvider({})

        async def _fake_run_sync(func, *args, **kwargs):
            return func(*args, **kwargs)

        monkeypatch.setattr(
            "backend.plugins.cloud_integration.providers.aliyun._run_sync",
            _fake_run_sync,
        )
        provider._do_action = lambda _req: {}
        provider._instances["i1"] = {
            "instance_id": "i1",
            "gpu_type": "A100",
            "status": "pending",
            "started_at": None,
            "stopped_at": None,
        }
        started = await provider.start_instance("i1")
        assert started["status"] == "running"
        stopped = await provider.stop_instance("i1")
        assert stopped["status"] == "stopped"
        assert await provider.get_cost("none", "1", "2") == 0.0
        cost = await provider.get_cost("i1", "0", "3600")
        assert cost >= 0

    async def test_get_instance_status_unknown(self, monkeypatch):
        provider = AliyunProvider({})
        monkeypatch.setattr(
            "backend.plugins.cloud_integration.providers.aliyun._run_sync",
            lambda func, *args, **kwargs: (_ for _ in ()).throw(RuntimeError("x")),
        )
        status = await provider.get_instance_status("i-x")
        assert status["status"] == "unknown"
