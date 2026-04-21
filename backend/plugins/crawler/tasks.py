"""Crawler plugin — 定时任务调度。

使用 APScheduler 的 AsyncIOScheduler 管理周期性爬虫任务。
任务在应用启动时从数据库恢复并重新注册到调度器。
"""

from __future__ import annotations

import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()


async def _run_crawl_task(task_id: uuid.UUID):
    """APScheduler 调用的实际执行函数。"""
    crawler_service = None
    # 通过容器获取（需要在运行时获取）
    # APScheduler 回调在 async 事件循环中执行，直接调用服务
    try:
        # 延迟导入避免循环
        from backend.core.container import container as global_container

        crawler_service = global_container.get("crawler")
    except Exception:
        return

    try:
        await crawler_service.execute_task(task_id)
    except Exception:
        # 执行失败，标记为 failed
        try:
            await crawler_service.update_task_status(task_id, "failed")
        except Exception:
            pass


def init_scheduler() -> AsyncIOScheduler:
    """初始化调度器并恢复已注册的定时任务。

    在 plugin on_startup 钩子中调用，此时容器和服务已就绪。
    """
    if scheduler.running:
        return scheduler

    # 从数据库恢复有调度间隔的任务
    import asyncio

    from sqlalchemy import select

    from backend.plugins.crawler.models import CrawlTask

    # 获取 session_factory（需要从容器获取 db）
    # 由于此时可能尚未完全初始化，使用延迟加载
    try:
        from backend.core.container import container as global_container

        db = global_container.get("db")
        session_factory = db["session_factory"]

        async def _restore_tasks():
            async with session_factory() as session:
                result = await session.execute(
                    select(CrawlTask).where(
                        CrawlTask.schedule_interval > 0,
                        CrawlTask.status.in_(["pending", "running"]),
                    )
                )
                tasks = result.scalars().all()

                for task in tasks:
                    task_id = task.id
                    interval_hours = task.schedule_interval
                    scheduler.add_job(
                        _run_crawl_task,
                        trigger=IntervalTrigger(hours=interval_hours),
                        args=[task_id],
                        id=f"crawl_{task_id}",
                        replace_existing=True,
                        name=f"定时抓取: {task.name}",
                    )

        # 在已运行的事件循环中执行恢复
        try:
            asyncio.get_running_loop()
            asyncio.ensure_future(_restore_tasks())
        except RuntimeError:
            # 没有运行中的事件循环
            pass
    except Exception:
        pass

    scheduler.start()
    return scheduler


def schedule_task(task_id: uuid.UUID, interval_hours: int) -> None:
    """将单个任务注册到调度器。"""
    scheduler.add_job(
        _run_crawl_task,
        trigger=IntervalTrigger(hours=interval_hours),
        args=[task_id],
        id=f"crawl_{task_id}",
        replace_existing=True,
    )


def unschedule_task(task_id: uuid.UUID) -> None:
    """从调度器移除任务。"""
    job_id = f"crawl_{task_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
