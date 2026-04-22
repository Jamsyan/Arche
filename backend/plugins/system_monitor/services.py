"""System Monitor Service — 基于 psutil 的系统资源采集与历史数据管理。"""

from __future__ import annotations

import sys
import time
from collections import deque
from typing import TYPE_CHECKING

import psutil
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

if TYPE_CHECKING:
    from backend.core.container import ServiceContainer


class SystemMonitorService:
    MAX_HISTORY = 300

    def __init__(self, container: "ServiceContainer"):
        self.container = container
        config = container.get("config")
        self._collect_interval = config.get("MONITOR_COLLECT_INTERVAL", 10)

        self._scheduler: AsyncIOScheduler | None = None
        self._history: deque = deque(maxlen=self.MAX_HISTORY)
        self._last_net = psutil.net_io_counters()

    # --- 采集控制 ---
    def start_collection(self) -> None:
        if self._scheduler:
            return
        self._scheduler = AsyncIOScheduler()
        self._scheduler.add_job(
            self._collect_snapshot,
            trigger=IntervalTrigger(seconds=self._collect_interval),
            id="system_monitor_collect",
            replace_existing=True,
        )
        self._scheduler.start()

    def stop_collection(self) -> None:
        if self._scheduler and getattr(self._scheduler, "running", False):
            self._scheduler.shutdown(wait=False)
            self._scheduler = None

    async def _collect_snapshot(self) -> None:
        """定时采集系统快照。"""
        net = psutil.net_io_counters()
        net_diff_sent = net.bytes_sent - self._last_net.bytes_sent
        net_diff_recv = net.bytes_recv - self._last_net.bytes_recv
        self._last_net = net

        try:
            load = list(psutil.getloadavg())
        except (OSError, NotImplementedError):
            load = [0.0, 0.0, 0.0]

        snapshot = {
            "ts": time.time(),
            "cpu_pct": psutil.cpu_percent(interval=0),
            "cpu_count": psutil.cpu_count(),
            "mem_total": psutil.virtual_memory().total,
            "mem_used": psutil.virtual_memory().used,
            "mem_pct": psutil.virtual_memory().percent,
            "disk_total": psutil.disk_usage("/").total,
            "disk_used": psutil.disk_usage("/").used,
            "disk_pct": psutil.disk_usage("/").percent,
            "net_sent_rate": net_diff_sent / self._collect_interval,
            "net_recv_rate": net_diff_recv / self._collect_interval,
            "load_1": load[0],
            "load_5": load[1],
            "load_15": load[2],
        }
        self._history.append(snapshot)

    # --- 查询接口（同步） ---
    def get_summary(self) -> dict:
        """系统概览。"""
        try:
            load = list(psutil.getloadavg())
        except (OSError, NotImplementedError):
            load = [0.0, 0.0, 0.0]

        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        return {
            "cpu_percent": psutil.cpu_percent(interval=0),
            "cpu_count": psutil.cpu_count(),
            "memory_used_gb": round(mem.used / 1024**3, 2),
            "memory_total_gb": round(mem.total / 1024**3, 2),
            "memory_percent": mem.percent,
            "disk_used_gb": round(disk.used / 1024**3, 2),
            "disk_total_gb": round(disk.total / 1024**3, 2),
            "disk_percent": disk.percent,
            "net_sent": net.bytes_sent,
            "net_recv": net.bytes_recv,
            "process_count": len(psutil.pids()),
            "python_version": sys.version.split()[0],
            "uptime": time.time() - psutil.boot_time(),
            "platform": sys.platform,
            "load_1": load[0],
            "load_5": load[1],
            "load_15": load[2],
        }

    def get_cpu_detail(self) -> dict:
        """CPU 详细信息。"""
        freq = psutil.cpu_freq()
        try:
            load = list(psutil.getloadavg())
        except (OSError, NotImplementedError):
            load = [0.0, 0.0, 0.0]

        return {
            "count_physical": psutil.cpu_count(logical=False),
            "count_logical": psutil.cpu_count(logical=True),
            "freq_current": freq.current if freq else None,
            "freq_min": freq.min if freq else None,
            "freq_max": freq.max if freq else None,
            "per_cpu_pct": psutil.cpu_percent(interval=0, percpu=True),
            "load_1": load[0],
            "load_5": load[1],
            "load_15": load[2],
        }

    def get_memory_detail(self) -> dict:
        """内存详细信息。"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "free": mem.free,
            "percent": mem.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_free": swap.free,
            "swap_percent": swap.percent,
        }

    def get_disk_detail(self) -> dict:
        """磁盘详细信息（按分区）。"""
        usage = psutil.disk_usage("/")
        partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                u = psutil.disk_usage(part.mountpoint)
                partitions.append(
                    {
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total": u.total,
                        "used": u.used,
                        "free": u.free,
                        "percent": u.percent,
                    }
                )
            except (PermissionError, OSError):
                pass

        return {
            "root_total": usage.total,
            "root_used": usage.used,
            "root_free": usage.free,
            "root_percent": usage.percent,
            "partitions": partitions,
        }

    def get_network_io(self) -> dict:
        """网络 I/O。"""
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "errin": net.errin,
            "errout": net.errout,
            "dropin": net.dropin,
            "dropout": net.dropout,
        }

    def get_history(self, page: int = 1, page_size: int = 50) -> dict:
        """历史数据分页查询。"""
        total = len(self._history)
        start = max(0, total - page * page_size)
        end = total - (page - 1) * page_size
        items = list(self._history)[start:end]
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_processes(self, sort_by: str = "cpu", limit: int = 50) -> dict:
        """进程列表，按指定字段排序。"""
        procs = []
        for proc in psutil.process_iter(
            ["pid", "name", "status", "cpu_percent", "memory_percent", "create_time"]
        ):
            try:
                info = proc.info
                procs.append(
                    {
                        "pid": info["pid"],
                        "name": info["name"] or "unknown",
                        "status": info["status"],
                        "cpu_percent": info["cpu_percent"] or 0.0,
                        "memory_percent": round(info["memory_percent"] or 0.0, 2),
                        "create_time": info["create_time"],
                    }
                )
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                pass

        reverse = True
        key = (
            sort_by
            if sort_by in ("cpu_percent", "memory_percent", "pid", "create_time")
            else "cpu_percent"
        )
        procs.sort(key=lambda p: p[key], reverse=reverse)

        return {"items": procs[:limit], "total": len(procs), "limit": limit}
