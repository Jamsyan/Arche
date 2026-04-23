"""Blog plugin — service layer."""

from __future__ import annotations

import io
import re
import uuid
from pathlib import Path

from sqlalchemy import delete, func, select
from fastapi import UploadFile

from backend.core.middleware import AppError

from .models import BlogPost, BlogComment, BlogLike, BlogReport, BlogTag, BlogPostTag

MAX_TAGS_PER_POST = 50

# A 等级 → 最大可见用户 P 等级（数字越小权限越高）
# A0=仅P0, A1=P0-P1, A2=P0-P2, A3=P0-P3, A4=P0-P4, A5+=所有人
ACCESS_LEVEL_MAP = {
    "A0": 0,
    "A1": 1,
    "A2": 2,
    "A3": 3,
    "A4": 4,
    "A5": 5,
    "A6": 5,
    "A7": 5,
    "A8": 5,
    "A9": 5,
}


def get_max_visible_p_level(access_level: str) -> int:
    """获取帖子 A 等级对应的最大可见 P 等级。"""
    return ACCESS_LEVEL_MAP.get(access_level.upper(), 5)


def can_user_see_post(access_level: str, user_level: int) -> bool:
    """判断用户是否有权限查看帖子。"""
    max_p = get_max_visible_p_level(access_level)
    return user_level <= max_p


def get_access_level_filter(user_level: int) -> list[str]:
    """根据用户等级生成 SQL 过滤条件（access_level 列表）。"""
    # 用户能看到所有 access_level 对应的 max_visible_p >= user_level 的帖子
    allowed = [al for al, max_p in ACCESS_LEVEL_MAP.items() if max_p >= user_level]
    return allowed


class BlogService:
    """博客服务：帖子 CRUD、评论、点赞、审核、举报。"""

    def __init__(self, container):
        self.container = container
        db = container.get("db")
        self.session_factory = db["session_factory"]

    # --- Slug 生成 ---

    async def generate_slug(self, title: str, exclude_slug: str | None = None) -> str:
        """异步生成唯一 slug。"""
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
        user_level: int | None = None,
    ) -> dict:
        """获取帖子列表（公开，分页）。"""
        offset = (page - 1) * page_size

        from backend.plugins.auth.models import User

        async with self.session_factory() as session:
            query = select(BlogPost)
            if status_filter:
                query = query.where(BlogPost.status == status_filter)

            # 权限过滤
            if user_level is not None:
                allowed_levels = get_access_level_filter(user_level)
                query = query.where(BlogPost.access_level.in_(allowed_levels))

            # 总数
            count_query = select(func.count()).select_from(BlogPost)
            if status_filter:
                count_query = count_query.where(BlogPost.status == status_filter)
            if user_level is not None:
                allowed_levels = get_access_level_filter(user_level)
                count_query = count_query.where(
                    BlogPost.access_level.in_(allowed_levels)
                )
            total_result = await session.execute(count_query)
            total = total_result.scalar_one()

            # 排序
            order_col = getattr(BlogPost, sort_by, BlogPost.created_at)
            query = query.order_by(order_col.desc())
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            posts = result.scalars().all()

            # 批量获取作者信息和点赞数
            if posts:
                author_ids = [p.author_id for p in posts]
                author_result = await session.execute(
                    select(User.id, User.username).where(User.id.in_(author_ids))
                )
                author_map = {row.id: row.username for row in author_result.all()}

                likes_result = await session.execute(
                    select(BlogLike.post_id, func.count(BlogLike.id))
                    .where(BlogLike.post_id.in_([p.id for p in posts]))
                    .group_by(BlogLike.post_id)
                )
                likes_map = {row.post_id: row.count for row in likes_result.all()}
            else:
                author_map = {}
                likes_map = {}

            return {
                "items": [
                    self._post_to_dict(
                        p,
                        author_username=author_map.get(p.author_id),
                        likes_count=likes_map.get(p.id, 0),
                    )
                    for p in posts
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def get_post_by_slug(self, slug: str, user_level: int | None = None) -> dict:
        """根据 slug 获取帖子详情（公开）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.slug == slug)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)

            # 权限检查
            if user_level is not None and not can_user_see_post(
                post.access_level, user_level
            ):
                raise AppError(
                    "无权查看此帖子", code="permission_denied", status_code=403
                )

            # 增加浏览量
            post.views += 1
            await session.commit()
            await session.refresh(post)

            post_dict = self._post_to_dict(post)
            post_dict["tags"] = await self.get_post_tags(post.id)
            return post_dict

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

    async def get_post_detail_by_id(
        self, post_id: uuid.UUID, user_level: int | None = None
    ) -> dict:
        """根据 ID 获取帖子详情（含标签，按权限过滤）。"""
        post = await self.get_post_by_id(post_id)

        # 权限检查
        if user_level is not None and not can_user_see_post(
            post.access_level, user_level
        ):
            raise AppError("无权查看此帖子", code="permission_denied", status_code=403)

        post_dict = self._post_to_dict(post)
        post_dict["tags"] = await self.get_post_tags(post.id)
        return post_dict

    async def create_post(
        self,
        author_id: uuid.UUID,
        title: str,
        content: str,
        tags: list[str] | None = None,
        access_level: str = "A5",
        user_level: int = 5,
    ) -> dict:
        """创建帖子，默认进入审核队列（status=pending）。"""
        from backend.plugins.auth.models import User
        from backend.plugins.blog.sensitive_words import get_filter

        # 权限等级验证
        al_num = (
            int(access_level.upper().lstrip("A"))
            if access_level.upper().startswith("A")
            else 5
        )
        if al_num < user_level:
            raise AppError(
                f"无权设置 {access_level.upper()} 权限，最高可设置 A{user_level}",
                code="access_level_too_high",
                status_code=403,
            )

        # 敏感词检查
        word_filter = get_filter()
        passed, matched_words = word_filter.check(title + " " + content)
        if not passed:
            raise AppError(
                f"内容包含敏感词: {', '.join(matched_words)}",
                code="sensitive_word",
                status_code=400,
            )

        slug_base = re.sub(r"[^\w一-鿿-]", "-", title.lower().strip())
        slug_base = re.sub(r"-+", "-", slug_base).strip("-") or "post"

        async with self.session_factory() as session:
            # 生成唯一 slug（同一 session 内查询）
            result = await session.execute(
                select(BlogPost).where(BlogPost.slug == slug_base)
            )
            existing = result.scalar_one_or_none()
            slug = slug_base
            if existing:
                counter = 1
                while True:
                    candidate = f"{slug_base}-{counter}"
                    result = await session.execute(
                        select(BlogPost).where(BlogPost.slug == candidate)
                    )
                    if not result.scalar_one_or_none():
                        slug = candidate
                        break
                    counter += 1

            post = BlogPost(
                author_id=author_id,
                title=title,
                slug=slug,
                content=content,
                status="pending",
                access_level=access_level.upper(),
            )
            session.add(post)
            await session.flush()  # 获取 post.id

            # 处理标签（同一 session）
            if tags:
                for tag_name in tags[:MAX_TAGS_PER_POST]:
                    normalized_name = tag_name.strip().lower()
                    if not normalized_name:
                        continue
                    tag_result = await session.execute(
                        select(BlogTag).where(
                            func.lower(BlogTag.name) == normalized_name
                        )
                    )
                    tag = tag_result.scalar_one_or_none()
                    if not tag:
                        try:
                            tag = BlogTag(name=normalized_name)
                            session.add(tag)
                            await session.flush()
                        except Exception:
                            # 并发插入导致冲突，重新查询
                            await session.rollback()
                            tag_result = await session.execute(
                                select(BlogTag).where(
                                    func.lower(BlogTag.name) == normalized_name
                                )
                            )
                            tag = tag_result.scalar_one_or_none()
                            if not tag:
                                continue
                    session.add(BlogPostTag(post_id=post.id, tag_id=tag.id))

            await session.commit()
            await session.refresh(post)

            # 获取作者名
            author_result = await session.execute(
                select(User.username).where(User.id == author_id)
            )
            author_row = author_result.scalar_one_or_none()
            author_username = author_row.username if author_row else None

            result = self._post_to_dict(post, author_username=author_username)
            result["tags"] = await self.get_post_tags(post.id)
            return result

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
                raise AppError(
                    "无权限编辑此帖子", code="permission_denied", status_code=403
                )

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
                raise AppError(
                    "无权限删除此帖子", code="permission_denied", status_code=403
                )

            # 删除关联数据
            await session.execute(
                delete(BlogComment).where(BlogComment.post_id == post_id)
            )
            await session.execute(delete(BlogLike).where(BlogLike.post_id == post_id))
            await session.execute(
                delete(BlogReport).where(BlogReport.post_id == post_id)
            )
            await session.execute(
                delete(BlogPostTag).where(BlogPostTag.post_id == post_id)
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

        from backend.plugins.auth.models import User

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

            # 批量获取作者信息
            if comments:
                author_ids = [c.author_id for c in comments]
                author_result = await session.execute(
                    select(User.id, User.username).where(User.id.in_(author_ids))
                )
                author_map = {row.id: row.username for row in author_result.all()}
            else:
                author_map = {}

            return {
                "items": [
                    self._comment_to_dict(
                        c, author_username=author_map.get(c.author_id)
                    )
                    for c in comments
                ],
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

        async with self.session_factory() as session:
            # 如果有 parent_id，验证父评论存在且属于同一帖子
            if parent_id is not None:
                result = await session.execute(
                    select(BlogComment).where(
                        BlogComment.id == parent_id,
                        BlogComment.post_id == post_id,
                    )
                )
                if not result.scalar_one_or_none():
                    raise AppError(
                        "父评论不存在", code="parent_comment_not_found", status_code=404
                    )

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
        from backend.plugins.auth.models import User

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

            # 批量获取作者信息
            if posts:
                author_ids = [p.author_id for p in posts]
                author_result = await session.execute(
                    select(User.id, User.username).where(User.id.in_(author_ids))
                )
                author_map = {row.id: row.username for row in author_result.all()}
            else:
                author_map = {}

            return {
                "items": [
                    self._post_to_dict(p, author_username=author_map.get(p.author_id))
                    for p in posts
                ],
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

    # --- 标签 ---

    async def list_tags(
        self,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """获取标签列表（公开）。"""
        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            count_result = await session.execute(
                select(func.count()).select_from(BlogTag)
            )
            total = count_result.scalar_one()

            result = await session.execute(
                select(BlogTag)
                .order_by(BlogTag.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            tags = result.scalars().all()

            return {
                "items": [self._tag_to_dict(t) for t in tags],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def create_tag(self, name: str) -> dict:
        """创建标签。"""
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise AppError("标签名不能为空", code="empty_tag_name", status_code=400)
        if len(normalized_name) > 64:
            raise AppError("标签名过长", code="tag_name_too_long", status_code=400)

        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogTag).where(func.lower(BlogTag.name) == normalized_name)
            )
            existing = result.scalar_one_or_none()
            if existing:
                return self._tag_to_dict(existing)

            tag = BlogTag(name=normalized_name)
            session.add(tag)
            try:
                await session.commit()
            except Exception:
                # 并发插入导致冲突，重新查询
                await session.rollback()
                result = await session.execute(
                    select(BlogTag).where(func.lower(BlogTag.name) == normalized_name)
                )
                existing = result.scalar_one_or_none()
                if existing:
                    return self._tag_to_dict(existing)
                raise

            await session.refresh(tag)
            return self._tag_to_dict(tag)

    async def get_tag_by_name(self, name: str) -> BlogTag | None:
        """根据名称获取标签。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogTag).where(func.lower(BlogTag.name) == name.strip().lower())
            )
            return result.scalar_one_or_none()

    async def get_posts_by_tag(
        self,
        tag_name: str,
        page: int = 1,
        page_size: int = 20,
        user_level: int | None = None,
    ) -> dict:
        """按标签查询帖子列表。"""
        tag = await self.get_tag_by_name(tag_name)
        if not tag:
            raise AppError("标签不存在", code="tag_not_found", status_code=404)

        offset = (page - 1) * page_size

        async with self.session_factory() as session:
            count_query = (
                select(func.count())
                .select_from(BlogPostTag)
                .join(BlogPost, BlogPost.id == BlogPostTag.post_id)
                .where(
                    BlogPostTag.tag_id == tag.id,
                    BlogPost.status == "published",
                )
            )
            if user_level is not None:
                allowed_levels = get_access_level_filter(user_level)
                count_query = count_query.where(
                    BlogPost.access_level.in_(allowed_levels)
                )
            total = (await session.execute(count_query)).scalar_one()

            query = (
                select(BlogPost)
                .join(BlogPostTag, BlogPost.id == BlogPostTag.post_id)
                .where(
                    BlogPostTag.tag_id == tag.id,
                    BlogPost.status == "published",
                )
                .order_by(BlogPost.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            if user_level is not None:
                allowed_levels = get_access_level_filter(user_level)
                query = query.where(BlogPost.access_level.in_(allowed_levels))
            result = await session.execute(query)
            posts = result.scalars().all()

            return {
                "tag": self._tag_to_dict(tag),
                "items": [self._post_to_dict(p) for p in posts],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    async def add_tag_to_post(
        self,
        post_id: uuid.UUID,
        tag_name: str,
        user_id: uuid.UUID,
    ) -> dict:
        """给帖子添加标签（仅作者或 P0）。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)
            if post.author_id != user_id:
                raise AppError(
                    "无权限操作此帖子", code="permission_denied", status_code=403
                )

            # 检查标签数量上限
            tag_count_result = await session.execute(
                select(func.count())
                .select_from(BlogPostTag)
                .where(BlogPostTag.post_id == post_id)
            )
            tag_count = tag_count_result.scalar_one()
            if tag_count >= MAX_TAGS_PER_POST:
                raise AppError(
                    f"帖子标签数已达上限 ({MAX_TAGS_PER_POST})",
                    code="too_many_tags",
                    status_code=400,
                )

        # 获取或创建标签
        tag = await self.get_tag_by_name(tag_name)
        if not tag:
            tag_dict = await self.create_tag(tag_name)
            tag_id = uuid.UUID(tag_dict["id"])
        else:
            tag_dict = self._tag_to_dict(tag)
            tag_id = tag.id

        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPostTag).where(
                    BlogPostTag.post_id == post_id,
                    BlogPostTag.tag_id == tag_id,
                )
            )
            if result.scalar_one_or_none():
                raise AppError("标签已存在", code="tag_already_exists", status_code=400)

            post_tag = BlogPostTag(post_id=post_id, tag_id=tag_id)
            session.add(post_tag)
            await session.commit()

            return {"tag": tag, "post_id": str(post_id)}

    async def remove_tag_from_post(
        self,
        post_id: uuid.UUID,
        tag_name: str,
        user_id: uuid.UUID,
    ) -> None:
        """从帖子移除标签（仅作者或 P0）。"""
        tag = await self.get_tag_by_name(tag_name)
        if not tag:
            raise AppError("标签不存在", code="tag_not_found", status_code=404)

        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            if not post:
                raise AppError("帖子不存在", code="post_not_found", status_code=404)
            if post.author_id != user_id:
                raise AppError(
                    "无权限操作此帖子", code="permission_denied", status_code=403
                )

            result = await session.execute(
                select(BlogPostTag).where(
                    BlogPostTag.post_id == post_id,
                    BlogPostTag.tag_id == tag.id,
                )
            )
            post_tag = result.scalar_one_or_none()
            if not post_tag:
                raise AppError("帖子无此标签", code="tag_not_on_post", status_code=400)

            await session.delete(post_tag)
            await session.commit()

    async def get_post_tags(self, post_id: uuid.UUID) -> list[dict]:
        """获取帖子的所有标签。"""
        async with self.session_factory() as session:
            result = await session.execute(
                select(BlogTag)
                .join(BlogPostTag, BlogTag.id == BlogPostTag.tag_id)
                .where(BlogPostTag.post_id == post_id)
                .order_by(BlogTag.name)
            )
            tags = result.scalars().all()
            return [self._tag_to_dict(t) for t in tags]

    # --- 文件导入 ---

    ALLOWED_IMPORT_TYPES = {".md", ".txt", ".docx", ".html", ".htm"}

    async def import_post(
        self,
        file: UploadFile,
        author_id: uuid.UUID,
        user_level: int = 5,
        access_level: str = "A5",
        tags: list[str] | None = None,
    ) -> dict:
        """从文件导入帖子。"""
        filename = file.filename or ""
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_IMPORT_TYPES:
            allowed = ", ".join(sorted(self.ALLOWED_IMPORT_TYPES))
            raise AppError(
                f"不支持的文件类型: {ext}，支持 {allowed}",
                code="unsupported_file_type",
                status_code=400,
            )

        content = await file.read()

        # 解析文件内容
        if ext == ".md" or ext == ".txt":
            text = content.decode("utf-8", errors="replace")
        elif ext == ".html" or ext == ".htm":
            text = content.decode("utf-8", errors="replace")
            text = self._extract_html_body(text)
        elif ext == ".docx":
            text = await self._parse_docx(content)
        else:
            text = content.decode("utf-8", errors="replace")

        # 从内容提取标题（第一个 # heading 或文件名）
        title, body = self._extract_title(text, filename)

        return await self.create_post(
            author_id=author_id,
            title=title,
            content=body,
            tags=tags,
            access_level=access_level,
            user_level=user_level,
        )

    def _extract_title(self, text: str, fallback_filename: str) -> tuple[str, str]:
        """从 Markdown 文本中提取标题。"""
        match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            # 移除标题行
            body = re.sub(r"^#\s+.+$\n?", "", text, count=1, flags=re.MULTILINE).strip()
            return title, body
        # 没有标题，用文件名作为标题
        name = Path(fallback_filename).stem or "导入的帖子"
        return name, text.strip()

    def _extract_html_body(self, html: str) -> str:
        """从 HTML 中提取 body 内容并转为简单 Markdown。"""
        import html as html_mod

        # 提取 body
        match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
        text = match.group(1) if match else html

        # 简单转换：heading, paragraph, br
        text = re.sub(
            r"<h1[^>]*>(.*?)</h1>", r"# \1\n", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<h2[^>]*>(.*?)</h2>", r"## \1\n", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(
            r"<h3[^>]*>(.*?)</h3>", r"### \1\n", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(
            r"<p[^>]*>(.*?)</p>", r"\1\n\n", text, flags=re.IGNORECASE | re.DOTALL
        )
        text = re.sub(r"<[^>]+>", "", text)
        text = html_mod.unescape(text)
        return text.strip()

    async def _parse_docx(self, content: bytes) -> str:
        """解析 .docx 文件内容为文本。"""
        try:
            from docx import Document
        except ImportError:
            raise AppError(
                "python-docx 未安装，无法解析 .docx 文件",
                code="missing_dependency",
                status_code=500,
            )

        doc = Document(io.BytesIO(content))
        parts = []
        for para in doc.paragraphs:
            if para.style and para.style.name and para.style.name.startswith("Heading"):
                level = para.style.name.replace("Heading ", "")
                prefix = "#" * int(level) if level.isdigit() else "#"
                parts.append(f"{prefix} {para.text}")
            else:
                parts.append(para.text)
        return "\n\n".join(p for p in parts if p.strip())

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

    def _tag_to_dict(self, tag: BlogTag) -> dict:
        return {
            "id": str(tag.id),
            "name": tag.name,
            "created_at": tag.created_at.isoformat() if tag.created_at else None,
        }

    def _post_to_dict(
        self,
        post: BlogPost,
        *,
        author_username: str | None = None,
        likes_count: int = 0,
    ) -> dict:
        return {
            "id": str(post.id),
            "author_id": str(post.author_id),
            "author_username": author_username or str(post.author_id)[:8],
            "title": post.title,
            "slug": post.slug,
            "content": post.content,
            "status": post.status,
            "quality_score": post.quality_score,
            "views": post.views,
            "likes": likes_count,
            "access_level": post.access_level,
            "created_at": post.created_at.isoformat() if post.created_at else None,
        }

    def _comment_to_dict(
        self, comment: BlogComment, *, author_username: str | None = None
    ) -> dict:
        return {
            "id": str(comment.id),
            "post_id": str(comment.post_id),
            "author_id": str(comment.author_id),
            "author_username": author_username or str(comment.author_id)[:8],
            "content": comment.content,
            "parent_id": str(comment.parent_id) if comment.parent_id else None,
            "created_at": comment.created_at.isoformat()
            if comment.created_at
            else None,
        }

    def _report_to_dict(self, report: BlogReport) -> dict:
        return {
            "id": str(report.id),
            "post_id": str(report.post_id),
            "reporter_id": str(report.reporter_id),
            "reason": report.reason,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
