"""Crawler plugin — 业务逻辑：网页抓取、任务管理、结果存储。"""

from __future__ import annotations

import json
import uuid

import httpx
from sqlalchemy import func, select

from backend.core.middleware import AppError


class CrawlerService:
    """爬虫服务：任务 CRUD、网页抓取、结果管理。"""

    def __init__(self, container):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]

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
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Veil Crawler/0.1.0)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                },
            ) as client:
                response = await client.get(url)

                # 提取 title
                title = self._extract_title(response.text)

                # 提取纯文本内容（简易版，去掉 HTML 标签）
                content = self._extract_text(response.text)

                return {
                    "url": str(response.url),
                    "title": title,
                    "content": content,
                    "raw_html": response.text[:100000],  # 限制原始 HTML 长度
                    "status_code": response.status_code,
                    "headers": json.dumps(dict(response.headers), ensure_ascii=False),
                }
        except httpx.TimeoutException:
            raise AppError("请求超时", code="crawl_timeout", status_code=504)
        except httpx.HTTPStatusError as e:
            raise AppError(
                f"HTTP 错误: {e.response.status_code}",
                code="http_error",
                status_code=502,
            )
        except httpx.RequestError as e:
            raise AppError(
                f"请求失败: {e}", code="request_error", status_code=502
            )

    async def execute_task(self, task_id: uuid.UUID) -> list[dict]:
        """执行一个爬虫任务，抓取种子 URL 并存储结果。"""
        from backend.plugins.crawler.models import CrawlResult, CrawlTask

        async with self.session_factory() as session:
            result = await session.execute(
                select(CrawlTask).where(CrawlTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                raise AppError(
                    "任务不存在", code="task_not_found", status_code=404
                )

            if task.status == "running":
                raise AppError(
                    "任务正在运行中", code="task_running", status_code=409
                )

            # 更新状态为 running
            task.status = "running"
            await session.commit()

        seed_urls = json.loads(task.seed_urls)
        results = []

        for url in seed_urls:
            try:
                data = await self.crawl_url(url)

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
                    results.append(self._result_to_dict(crawl_result))
            except AppError:
                # 单个 URL 失败不影响其他 URL，记录失败但不中断
                continue

        # 更新任务状态为 completed
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
