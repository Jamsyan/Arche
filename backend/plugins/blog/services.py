"""Blog plugin — service layer."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select

from backend.core.middleware import AppError

from .models import BlogPost, BlogComment, BlogLike, BlogReport


class BlogService:
    """博客服务：帖子 CRUD、评论、点赞、审核、举报。"""

    def __init__(self, container):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]

    # --- Slug 生成 ---

    async def generate_slug(self, title: str, exclude_slug: str | None = None) -> str:
        """异步生成唯一 slug。"""
        import re

        slug = re.sub(r"[^\w一-鿿-]", "-", title.lower().strip())
        slug = re.sub(r"-+", "-", slug).strip("-")
        if not slug:
            slug = "post"

        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.slug == slug)
            )
            existing = result.scalar_one_or_none()

        if existing and existing.slug != (exclude_slug or ""):
            counter = 1
            while True:
                candidate = f"{slug}-{counter}"
                async with self.session_factory() as session:
                    result = await session.execute(
                        select(BlogPost).where(BlogPost.slug == candidate)
                    )
                    if not result.scalar_one_or_none():
                        return candidate
                    counter += 1

        return slug

    # --- 帖子 CRUD ---

    async def list_posts(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = "published",
        sort_by: str = "created_at",
    ) -> dict:
        """获取帖子列表（公开，分页）。"""
        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            query = select(BlogPost)
            if status_filter:
                query = query.where(BlogPost.status == status_filter)

            # 总数
            count_query = select(func.count()).select_from(BlogPost)
            if status_filter:
                count_query = count_query.where(BlogPost.status == status_filter)
            total_result = await session.execute(count_query)
            total = total_result.scalar_one()

            # 排序
            order_col = getattr(BlogPost, sort_by, BlogPost.created_at)
            query = query.order_by(order_col.desc())
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            posts = result.scalars().all()

            return {
                "items": [self._post_to_dict(p) for p in posts],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def get_post_by_slug(self, slug: str) -> dict:
        """根据 slug 获取帖子详情（公开）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.slug == slug)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)

            # 增加浏览量
            post.views += 1
            await session.commit()
            await session.refresh(post)

            return self._post_to_dict(post)

    async def get_post_by_id(self, post_id: uuid.UUID) -> BlogPost:
        """根据 ID 获取帖子模型对象。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)
            return post

    async def create_post(
        self,
        author_id: uuid.UUID,
        title: str,
        content: str,
    ) -> dict:
        """创建帖子，默认进入审核队列（status=pending）。"""
        from backend.plugins.blog.sensitive_words import get_filter

        # 敏感词检查
        word_filter = get_filter()
        passed, matched_words = word_filter.check(title + " " + content)

        if not passed:
            # 包含敏感词 → 直接拒绝
            slug = await self.generate_slug(title)
            async with self.session_factory() as session:
                post = BlogPost(
                    author_id=author_id,
                    title=title,
                    slug=slug,
                    content=content,
                    status="rejected",
                )
                session.add(post)
                await session.commit()
                await session.refresh(post)
                return self._post_to_dict(post)

        slug = await self.generate_slug(title)

        async with self.session_factory() as session:
            post = BlogPost(
                author_id=author_id,
                title=title,
                slug=slug,
                content=content,
                status="pending",
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)

            return self._post_to_dict(post)

    async def update_post(
        self,
        post_id: uuid.UUID,
        author_id: uuid.UUID,
        title: str | None = None,
        content: str | None = None,
    ) -> dict:
        """编辑帖子（仅作者本人）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)
            if post.author_id != author_id:
                raise AppError("无权限编辑此帖子", code="permission_denied", status_code=403)

            if title is not None:
                post.title = title
                # 重新生成 slug
                post.slug = await self.generate_slug(title, exclude_slug=post.slug)
            if content is not None:
                post.content = content
            # 编辑后重新进入审核
            post.status = "pending"

            await session.commit()
            await session.refresh(post)

            return self._post_to_dict(post)

    async def delete_post(
        self,
        post_id: uuid.UUID,
        user_id: uuid.UUID,
        user_level: int,
    ) -> None:
        """删除帖子（作者本人 或 P0）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)

            if post.author_id != user_id and user_level != 0:
                raise AppError("无权限删除此帖子", code="permission_denied", status_code=403)

            # 删除关联数据
            await session.execute(
                BlogComment.__table__.delete().where(BlogComment.post_id == post_id)
            )
            await session.execute(
                BlogLike.__table__.delete().where(BlogLike.post_id == post_id)
            )
            await session.execute(
                BlogReport.__table__.delete().where(BlogReport.post_id == post_id)
            )
            await session.delete(post)
            await session.commit()

    # --- 评论 ---

    async def list_comments(
        self,
        post_id: uuid.UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """获取评论列表（公开）。"""
        # 验证帖子存在
        await self.get_post_by_id(post_id)

        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            count_result = await session.execute(
                select(func.count()).where(BlogComment.post_id == post_id)
            )
            total = count_result.scalar_one()

            result = await session.execute(
                select(BlogComment)
                .where(BlogComment.post_id == post_id)
                .order_by(BlogComment.created_at.asc())
                .offset(offset)
                .limit(page_size)
            )
            comments = result.scalars().all()

            return {
                "items": [self._comment_to_dict(c) for c in comments],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def create_comment(
        self,
        post_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
        parent_id: uuid.UUID | None = None,
    ) -> dict:
        """发表评论（需登录）。"""
        # 验证帖子存在
        await self.get_post_by_id(post_id)

        # 如果有 parent_id，验证父评论存在且属于同一帖子
        if parent_id is not None:
            async with self.session_factory() as session:
                result = await session.execute(
                    select(BlogComment).where(
                        BlogComment.id == parent_id,
                        BlogComment.post_id == post_id,
                    )
                )
                if not result.scalar_one_or_none():
                    raise AppError("父评论不存在", code="parent_comment_not_found", status_code=404)

        async with self.session_factory() as session:
            comment = BlogComment(
                post_id=post_id,
                author_id=author_id,
                content=content,
                parent_id=parent_id,
            )
            session.add(comment)
            await session.commit()
            await session.refresh(comment)

            return self._comment_to_dict(comment)

    # --- 点赞 ---

    async def toggle_like(
        self,
        post_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dict:
        """点赞（幂等，重复调用取消点赞）。"""
        # 验证帖子存在
        await self.get_post_by_id(post_id)

        async with self.session_factory() as session:
            # 检查是否已点赞
            result = await session.execute(
                select(BlogLike).where(
                    BlogLike.post_id == post_id,
                    BlogLike.user_id == user_id,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # 取消点赞
                await session.delete(existing)
                await session.commit()
                return {"action": "unliked"}

            # 点赞
            like = BlogLike(post_id=post_id, user_id=user_id)
            session.add(like)
            await session.commit()
            return {"action": "liked"}

    # --- 审核 ---

    async def list_pending_posts(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """获取待审核帖子列表（P0）。"""
        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            count_result = await session.execute(
                select(func.count()).where(BlogPost.status == "pending")
            )
            total = count_result.scalar_one()

            result = await session.execute(
                select(BlogPost)
                .where(BlogPost.status == "pending")
                .order_by(BlogPost.created_at.asc())
                .offset(offset)
                .limit(page_size)
            )
            posts = result.scalars().all()

            return {
                "items": [self._post_to_dict(p) for p in posts],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def approve_post(self, post_id: uuid.UUID) -> dict:
        """通过审核（P0）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)
            if post.status not in ("pending", "under_review"):
                raise AppError(
                    f"帖子状态为 {post.status}，无法审核",
                    code="invalid_status",
                    status_code=400,
                )

            post.status = "published"
            post.quality_score += 1
            await session.commit()
            await session.refresh(post)

            return self._post_to_dict(post)

    async def reject_post(self, post_id: uuid.UUID) -> dict:
        """拒绝审核（P0）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)
            if post.status not in ("pending", "under_review"):
                raise AppError(
                    f"帖子状态为 {post.status}，无法审核",
                    code="invalid_status",
                    status_code=400,
                )

            post.status = "rejected"
            post.quality_score = max(0, post.quality_score - 1)
            await session.commit()
            await session.refresh(post)

            return self._post_to_dict(post)

    # --- 举报 ---

    async def create_report(
        self,
        post_id: uuid.UUID,
        reporter_id: uuid.UUID,
        reason: str | None = None,
    ) -> dict:
        """举报帖子（需登录）。"""
        # 验证帖子存在
        await self.get_post_by_id(post_id)

        async with self.session_factory() as session:
            report = BlogReport(
                post_id=post_id,
                reporter_id=reporter_id,
                reason=reason,
            )
            session.add(report)

            # 举报触发风控：将帖子标记为 throttled（降流）
            result = await session.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = result.scalar_one()
            if post.status == "published":
                post.status = "throttled"

            await session.commit()
            await session.refresh(report)

            return self._report_to_dict(report)

    # --- 数据转换 ---

    def _post_to_dict(self, post: BlogPost) -> dict:
        return {
            "id": str(post.id),
            "author_id": str(post.author_id),
            "title": post.title,
            "slug": post.slug,
            "content": post.content,
            "status": post.status,
            "quality_score": post.quality_score,
            "views": post.views,
            "created_at": post.created_at.isoformat() if post.created_at else None,
        }

    def _comment_to_dict(self, comment: BlogComment) -> dict:
        return {
            "id": str(comment.id),
            "post_id": str(comment.post_id),
            "author_id": str(comment.author_id),
            "content": comment.content,
            "parent_id": str(comment.parent_id) if comment.parent_id else None,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
        }

    def _report_to_dict(self, report: BlogReport) -> dict:
        return {
            "id": str(report.id),
            "post_id": str(report.post_id),
            "reporter_id": str(report.reporter_id),
            "reason": report.reason,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
