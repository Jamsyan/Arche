"""Crawler plugin — 业务逻辑：Playwright 抓取、链接扩展、去重、限流、结果存储。"""

from __future__ import annotations

import asyncio
import json
import uuid

from sqlalchemy import func, select

from backend.core.middleware import AppError

from .link_extractor import extract_links
from .rate_limiter import RateLimiter
from .robots_checker import RobotsChecker
from .url_dedup import URLDedup


class CrawlerService:
    """爬虫服务：任务 CRUD、Playwright 抓取、链接扩展、去重、限流。"""

    def __init__(self, container):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]

        # 共享组件实例
        self._dedup = URLDedup()
        self._robots_checker = RobotsChecker()
        self._rate_limiter = RateLimiter()

    # --- BrowserManager 生命周期 ---
    async def set_browser_manager(self, browser_manager):
        """设置浏览器管理器（由插件 on_startup 注入）。"""
        self._browser_manager = browser_manager

    # --- 任务 CRUD ---

    async def create_task(
        self,
        name: str,
        seed_urls: list[str],
        schedule_interval: int = 0,
    ) -> dict:
        """创建爬虫任务。"""
        from backend.plugins.crawler.models import CrawlTask

        async with self.session_factory() as session:
            task = CrawlTask(
                name=name,
                seed_urls=json.dumps(seed_urls, ensure_ascii=False),
                schedule_interval=schedule_interval,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return self._task_to_dict(task)

    async def list_tasks(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
    ) -> dict:
        """获取任务列表（分页）。"""
        from backend.plugins.crawler.models import CrawlTask

        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            query = select(CrawlTask)
            count_query = select(func.count()).select_from(CrawlTask)

            if status_filter:
                query = query.where(CrawlTask.status == status_filter)
                count_query = count_query.where(CrawlTask.status == status_filter)

            total_result = await session.execute(count_query)
            total = total_result.scalar_one()

            query = query.order_by(CrawlTask.created_at.desc())
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            tasks = result.scalars().all()

            return {
                "items": [self._task_to_dict(t) for t in tasks],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def get_task(self, task_id: uuid.UUID) -> dict:
        """获取任务详情。"""
        from backend.plugins.crawler.models import CrawlTask

        async with self.session_factory() as session:
            result = await session.execute(
                select(CrawlTask).where(CrawlTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                raise AppError(
                    "任务不存在", code="task_not_found", status_code=404
                )
            return self._task_to_dict(task)

    async def update_task_status(
        self, task_id: uuid.UUID, status: str
    ) -> dict:
        """更新任务状态。"""
        from backend.plugins.crawler.models import CrawlTask

        valid_statuses = {"pending", "running", "paused", "completed", "failed"}
        if status not in valid_statuses:
            raise AppError(
                f"无效状态: {status}", code="invalid_status", status_code=400
            )

        async with self.session_factory() as session:
            result = await session.execute(
                select(CrawlTask).where(CrawlTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                raise AppError(
                    "任务不存在", code="task_not_found", status_code=404
                )

            task.status = status
            await session.commit()
            await session.refresh(task)

            return self._task_to_dict(task)

    async def delete_task(self, task_id: uuid.UUID) -> None:
        """删除任务及其关联结果。"""
        from backend.plugins.crawler.models import CrawlResult, CrawlTask

        async with self.session_factory() as session:
            # 先删除关联结果
            await session.execute(
                CrawlResult.__table__.delete().where(
                    CrawlResult.task_id == task_id
                )
            )
            # 再删除任务
            result = await session.execute(
                select(CrawlTask).where(CrawlTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                raise AppError(
                    "任务不存在", code="task_not_found", status_code=404
                )
            await session.delete(task)
            await session.commit()

    # --- 结果管理 ---

    async def list_results(
        self,
        task_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """获取任务的结果列表（分页）。"""
        from backend.plugins.crawler.models import CrawlResult, CrawlTask

        # 验证任务存在
        async with self.session_factory() as session:
            task_result = await session.execute(
                select(CrawlTask).where(CrawlTask.id == task_id)
            )
            if not task_result.scalar_one_or_none():
                raise AppError(
                    "任务不存在", code="task_not_found", status_code=404
                )

        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            count_result = await session.execute(
                select(func.count()).where(CrawlResult.task_id == task_id)
            )
            total = count_result.scalar_one()

            result = await session.execute(
                select(CrawlResult)
                .where(CrawlResult.task_id == task_id)
                .order_by(CrawlResult.crawled_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            items = result.scalars().all()

            return {
                "items": [self._result_to_dict(r) for r in items],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def get_result(self, result_id: uuid.UUID) -> dict:
        """获取单条结果详情。"""
        from backend.plugins.crawler.models import CrawlResult

        async with self.session_factory() as session:
            result = await session.execute(
                select(CrawlResult).where(CrawlResult.id == result_id)
            )
            item = result.scalar_one_or_none()
            if not item:
                raise AppError(
                    "结果不存在", code="result_not_found", status_code=404
                )
            return self._result_to_dict(item)

    # --- 抓取逻辑 ---

    async def crawl_url(self, url: str) -> dict:
        """抓取单个 URL，返回解析后的数据。"""
        # robots.txt 检查
        if not await self._robots_checker.is_allowed(url):
            raise AppError("robots.txt 禁止爬取", code="robots_disallowed", status_code=403)

        # Playwright 抓取
        browser_manager = getattr(self, "_browser_manager", None)
        if browser_manager:
            try:
                data = await browser_manager.fetch_page(url)
                return {
                    "url": data["final_url"],
                    "title": data["title"],
                    "content": data["text"],
                    "raw_html": data["html"][:100000],
                    "status_code": data["status_code"],
                    "headers": json.dumps(data["headers"], ensure_ascii=False),
                    "links": data["links"],
                }
            except Exception as e:
                raise AppError(f"浏览器抓取失败: {e}", code="crawl_error", status_code=502)
        else:
            # Fallback: httpx 简易抓取（无浏览器时）
            import httpx
            try:
                async with httpx.AsyncClient(
                    timeout=30.0,
                    follow_redirects=True,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Veil Crawler/0.1.0)",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    },
                ) as client:
                    response = await client.get(url)
                    html = response.text
                    # 提取 title
                    import re
                    title_match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
                    title = title_match.group(1).strip() if title_match else None
                    # 简易文本
                    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
                    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
                    text = re.sub(r"<[^>]+>", " ", text)
                    text = re.sub(r"\s+", " ", text).strip()[:10000]
                    # 提取链接
                    links = extract_links(html, str(response.url))

                    return {
                        "url": str(response.url),
                        "title": title,
                        "content": text,
                        "raw_html": html[:100000],
                        "status_code": response.status_code,
                        "headers": json.dumps(dict(response.headers), ensure_ascii=False),
                        "links": links,
                    }
            except httpx.TimeoutException:
                raise AppError("请求超时", code="crawl_timeout", status_code=504)
            except httpx.RequestError as e:
                raise AppError(f"请求失败: {e}", code="request_error", status_code=502)

    async def execute_task(self, task_id: uuid.UUID) -> list[dict]:
        """执行一个爬虫任务，支持链接扩展和并发控制。"""
        from backend.plugins.crawler.models import CrawlResult, CrawlTask

        async with self.session_factory() as session:
            result = await session.execute(
                select(CrawlTask).where(CrawlTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                raise AppError("任务不存在", code="task_not_found", status_code=404)

            if task.status == "running":
                raise AppError("任务正在运行中", code="task_running", status_code=409)

            task.status = "running"
            await session.commit()

        seed_urls = json.loads(task.seed_urls)
        max_depth = getattr(task, "max_depth", 1) or 1
        max_pages = getattr(task, "max_pages", 100) or 100
        concurrency = getattr(task, "concurrency", 3) or 3
        request_delay = getattr(task, "request_delay", 1) or 1
        respect_robots = bool(getattr(task, "respect_robots", 1))

        # 初始化组件
        self._dedup.clear()
        self._rate_limiter.update_interval(float(request_delay))

        # BFS 队列：(url, depth)
        queue: list[tuple[str, int]] = [(url, 0) for url in seed_urls if self._dedup.is_new(url)]
        for url, _ in queue:
            self._dedup.mark_seen(url)

        results = []
        semaphore = asyncio.Semaphore(concurrency)
        pages_crawled = 0

        async def _crawl_one(url: str, depth: int) -> list[dict]:
            nonlocal pages_crawled
            async with semaphore:
                # 速率限制
                await self._rate_limiter.wait(url)

                try:
                    data = await self.crawl_url(url)
                except AppError:
                    return []

                pages_crawled += 1

                # 存储结果
                async with self.session_factory() as session:
                    crawl_result = CrawlResult(
                        task_id=task_id,
                        url=data["url"],
                        title=data["title"],
                        content=data["content"],
                        raw_html=data["raw_html"],
                        status_code=data["status_code"],
                        headers=data["headers"],
                    )
                    session.add(crawl_result)
                    await session.commit()
                    await session.refresh(crawl_result)

                result_dict = self._result_to_dict(crawl_result)
                new_results = [result_dict]

                # 链接扩展：如果未达到最大深度和页数，提取新链接入队
                if depth < max_depth and pages_crawled < max_pages:
                    links = data.get("links", [])
                    for link in links:
                        if self._dedup.is_new(link) and pages_crawled < max_pages:
                            self._dedup.mark_seen(link)
                            queue.append((link, depth + 1))

                return new_results

        # 按批次处理队列
        batch_idx = 0
        while batch_idx < len(queue) and pages_crawled < max_pages:
            # 取出当前批次的 URL（不超过 concurrency * 2）
            batch_size = min(concurrency * 2, len(queue) - batch_idx, max_pages - pages_crawled)
            batch = queue[batch_idx : batch_idx + batch_size]
            batch_idx += batch_size

            # 并发执行
            tasks = [_crawl_one(url, depth) for url, depth in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in batch_results:
                if isinstance(r, list):
                    results.extend(r)

        # 更新任务状态
        async with self.session_factory() as session:
            result = await session.execute(
                select(CrawlTask).where(CrawlTask.id == task_id)
            )
            task = result.scalar_one()
            task.status = "completed"
            await session.commit()

        return results

    # --- 统计 ---

    async def get_stats(self) -> dict:
        """获取爬虫统计信息。"""
        from backend.plugins.crawler.models import CrawlResult, CrawlTask

        async with self.session_factory() as session:
            # 任务总数
            total_tasks_result = await session.execute(
                select(func.count()).select_from(CrawlTask)
            )
            total_tasks = total_tasks_result.scalar_one()

            # 按状态分组统计任务
            status_counts = {}
            status_result = await session.execute(
                select(CrawlTask.status, func.count(CrawlTask.id))
                .group_by(CrawlTask.status)
            )
            for row in status_result.all():
                status_counts[row[0]] = row[1]

            # 结果总数
            total_results_result = await session.execute(
                select(func.count()).select_from(CrawlResult)
            )
            total_results = total_results_result.scalar_one()

            return {
                "total_tasks": total_tasks,
                "tasks_by_status": status_counts,
                "total_results": total_results,
            }

    # --- 工具方法 ---

    def _task_to_dict(self, task) -> dict:
        return {
            "id": str(task.id),
            "name": task.name,
            "seed_urls": json.loads(task.seed_urls),
            "status": task.status,
            "schedule_interval": task.schedule_interval,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }

    def _result_to_dict(self, result) -> dict:
        return {
            "id": str(result.id),
            "task_id": str(result.task_id),
            "url": result.url,
            "title": result.title,
            "content": result.content,
            "status_code": result.status_code,
            "headers": json.loads(result.headers) if result.headers else None,
            "crawled_at": result.crawled_at.isoformat() if result.crawled_at else None,
        }

    @staticmethod
    def _extract_title(html: str) -> str | None:
        """从 HTML 中提取 title 标签内容。"""
        import re

        match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def _extract_text(html: str) -> str:
        """从 HTML 中提取纯文本（去掉标签，简易版）。"""
        import re

        # 去掉 script 和 style 标签内容
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        # 去掉所有 HTML 标签
        text = re.sub(r"<[^>]+>", " ", text)
        # 合并空白
        text = re.sub(r"\s+", " ", text).strip()
        # 限制长度
        return text[:10000] if len(text) > 10000 else text
