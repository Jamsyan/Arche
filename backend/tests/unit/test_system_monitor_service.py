"""SystemMonitorService tests with psutil mocked."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from backend.plugins.system_monitor import services as system_services
from backend.plugins.system_monitor.services import SystemMonitorService


def _service(monkeypatch):
    net = SimpleNamespace(
        bytes_sent=100,
        bytes_recv=200,
        packets_sent=3,
        packets_recv=4,
        errin=0,
        errout=0,
        dropin=0,
        dropout=0,
    )
    mem = SimpleNamespace(
        total=8 * 1024**3,
        used=2 * 1024**3,
        available=6 * 1024**3,
        free=5 * 1024**3,
        percent=25.0,
    )
    swap = SimpleNamespace(total=1024, used=256, free=768, percent=25.0)
    disk = SimpleNamespace(total=1000, used=400, free=600, percent=40.0)
    freq = SimpleNamespace(current=2400.0, min=1200.0, max=3600.0)
    part = SimpleNamespace(device="disk0", mountpoint="/", fstype="ext4")

    monkeypatch.setattr(system_services.psutil, "net_io_counters", lambda: net)
    monkeypatch.setattr(system_services.psutil, "virtual_memory", lambda: mem)
    monkeypatch.setattr(system_services.psutil, "swap_memory", lambda: swap)
    monkeypatch.setattr(system_services.psutil, "disk_usage", lambda path: disk)
    monkeypatch.setattr(system_services.psutil, "disk_partitions", lambda all=False: [part])
    monkeypatch.setattr(system_services.psutil, "cpu_percent", lambda interval=0, percpu=False: [1.0, 2.0] if percpu else 12.5)
    monkeypatch.setattr(system_services.psutil, "cpu_count", lambda logical=True: 8 if logical else 4)
    monkeypatch.setattr(system_services.psutil, "cpu_freq", lambda: freq)
    monkeypatch.setattr(system_services.psutil, "getloadavg", lambda: (0.1, 0.2, 0.3))
    monkeypatch.setattr(system_services.psutil, "pids", lambda: [1, 2])
    monkeypatch.setattr(system_services.psutil, "boot_time", lambda: 100.0)
    monkeypatch.setattr(system_services.time, "time", lambda: 200.0)

    container = MagicMock()
    container.get.return_value.get.return_value = "10"
    return SystemMonitorService(container)


class TestSystemMonitorService:
    def test_summary_cpu_memory_disk_and_network(self, monkeypatch):
        service = _service(monkeypatch)

        summary = service.get_summary()
        assert summary["cpu_percent"] == 12.5
        assert summary["memory_used_gb"] == 2.0
        assert summary["disk_percent"] == 40.0
        assert summary["net_sent"] == 100
        assert summary["load_15"] == 0.3

        cpu = service.get_cpu_detail()
        assert cpu["count_physical"] == 4
        assert cpu["freq_max"] == 3600.0

        memory = service.get_memory_detail()
        assert memory["swap_used"] == 256

        disk = service.get_disk_detail()
        assert disk["partitions"][0]["device"] == "disk0"

        network = service.get_network_io()
        assert network["packets_recv"] == 4

    @pytest.mark.asyncio
    async def test_history_collection_processes_and_scheduler(self, monkeypatch):
        service = _service(monkeypatch)

        class Proc:
            def __init__(self, info):
                self.info = info

        monkeypatch.setattr(
            system_services.psutil,
            "process_iter",
            lambda fields: [
                Proc(
                    {
                        "pid": 2,
                        "name": "python",
                        "status": "running",
                        "cpu_percent": 10.0,
                        "memory_percent": 5.555,
                        "create_time": 2.0,
                    }
                ),
                Proc(
                    {
                        "pid": 1,
                        "name": None,
                        "status": "sleeping",
                        "cpu_percent": None,
                        "memory_percent": None,
                        "create_time": 1.0,
                    }
                ),
            ],
        )

        await service._collect_snapshot()
        history = service.get_history(page=1, page_size=10)
        assert history["total"] == 1
        assert history["items"][0]["net_sent_rate"] == 0

        processes = service.get_processes(sort_by="pid", limit=1)
        assert processes["items"][0]["pid"] == 2
        assert processes["limit"] == 1

        scheduler = MagicMock()
        scheduler.running = True
        monkeypatch.setattr(system_services, "AsyncIOScheduler", lambda: scheduler)
        service.start_collection()
        service.start_collection()
        scheduler.add_job.assert_called_once()

        service.stop_collection()
        scheduler.shutdown.assert_called_once_with(wait=False)

    def test_load_average_and_disk_errors_fall_back(self, monkeypatch):
        service = _service(monkeypatch)
        monkeypatch.setattr(
            system_services.psutil,
            "getloadavg",
            MagicMock(side_effect=OSError("unsupported")),
        )
        monkeypatch.setattr(
            system_services.psutil,
            "disk_partitions",
            lambda all=False: [SimpleNamespace(device="bad", mountpoint="/bad", fstype="x")],
        )
        def disk_usage(path):
            if path == "/bad":
                raise OSError("denied")
            return SimpleNamespace(total=1, used=1, free=0, percent=100)

        monkeypatch.setattr(system_services.psutil, "disk_usage", disk_usage)

        assert service.get_summary()["load_1"] == 0.0
        assert service.get_cpu_detail()["load_5"] == 0.0
        assert service.get_disk_detail()["partitions"] == []
