"""博客种子数据脚本。

扫描 content/ 目录下的 markdown 文件（含 YAML frontmatter），
创建种子用户和帖子写入数据库。全部使用 raw SQL 以兼容 SQLite。

用法：
    uv run python -m backend.scripts.seed_blog              # 首次写入
    uv run python -m backend.scripts.seed_blog --reset       # 清空后重新写入
"""

from __future__ import annotations

import asyncio
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import init_db, Base
from backend.core.uid import make_sid

# ── 种子用户定义（固定 UUID）──────────────────────
SEED_USERS = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "username": "锦年志编辑部",
        "level": 0,
    },
    {"id": "00000000-0000-0000-0000-000000000002", "username": "林深", "level": 5},
    {"id": "00000000-0000-0000-0000-000000000003", "username": "阿野", "level": 5},
    {"id": "00000000-0000-0000-0000-000000000004", "username": "苏河", "level": 5},
    {"id": "00000000-0000-0000-0000-000000000005", "username": "南渡", "level": 5},
    {"id": "00000000-0000-0000-0000-000000000006", "username": "岚", "level": 5},
]

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


# ── Frontmatter 解析 ──────────────────────────────


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """解析 YAML frontmatter，返回 (meta, body)。"""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text.strip()

    meta: dict[str, object] = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kv = re.match(r"(\w+)\s*:\s*(.*)", line)
        if not kv:
            continue
        key, val = kv.group(1), kv.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [
                v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()
            ]
        elif val.isdigit():
            meta[key] = int(val)
        else:
            meta[key] = val.strip("'\"")

    return meta, match.group(2).strip()


def _parse_date(d: object) -> str:
    """返回 ISO 格式日期字符串（SQLite 兼容）。"""
    if isinstance(d, datetime):
        return d.isoformat()
    if isinstance(d, str):
        try:
            return (
                datetime.strptime(d, "%Y-%m-%d")
                .replace(tzinfo=timezone.utc)
                .isoformat()
            )
        except ValueError:
            pass
    return datetime.now(timezone.utc).isoformat()


def _make_slug(title: str) -> str:
    slug = re.sub(r"[^\w一-鿿-]", "-", title.lower().strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "post"


# ── 种子逻辑 ──────────────────────────────────────


async def seed_blog(reset: bool = False):
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")
    engine, _ = init_db(db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    user_map = {u["username"]: u["id"] for u in SEED_USERS}

    async with AsyncSession(engine) as session:
        # ── 重置 ──
        if reset:
            await session.execute(text("DELETE FROM blog_post_tags"))
            await session.execute(text("DELETE FROM blog_tags"))
            await session.execute(text("DELETE FROM blog_posts"))
            for u in SEED_USERS:
                await session.execute(
                    text("DELETE FROM users WHERE username = :name"),
                    {"name": u["username"]},
                )
            print("已清空种子数据。")

        # ── 用户 ──
        created_users = 0
        for u in SEED_USERS:
            exists = await session.execute(
                text("SELECT 1 FROM users WHERE username = :name"),
                {"name": u["username"]},
            )
            if exists.scalar():
                continue

            sid = make_sid("user", uuid.UUID(u["id"]))
            await session.execute(
                text(
                    "INSERT INTO users (id, sid, email, username, password_hash, level, blog_quality_level, is_active) "
                    "VALUES (:id, :sid, :email, :username, :pwd, :level, 0, 1)"
                ),
                {
                    "id": u["id"],
                    "sid": sid,
                    "email": f"seed-{u['username']}@arche.local",
                    "username": u["username"],
                    "pwd": "$2b$12$" + "x" * 53,
                    "level": u["level"],
                },
            )
            created_users += 1
        if created_users:
            await session.commit()
            print(f"  创建用户: {created_users}")

        # ── 帖子 ──
        md_files = sorted(CONTENT_DIR.glob("*.md"))
        if not md_files:
            print("⚠️  content/ 目录下没有找到 .md 文件。")
            return

        # 收集已用的 slug
        seen_result = await session.execute(text("SELECT slug FROM blog_posts"))
        used_slugs = set(row[0] for row in seen_result.fetchall())

        created_posts = 0
        created_tags: set[str] = set()

        for idx, md_file in enumerate(md_files):
            raw, body = _parse_frontmatter(md_file.read_text(encoding="utf-8"))

            title = str(raw.get("title", md_file.stem))
            author_id = user_map.get(str(raw.get("author", "锦年志编辑部")))
            if not author_id:
                print(f"  ⚠️  跳过 {md_file.name}：作者不存在")
                continue

            # slug 已存在则跳过（幂等）
            slug = _make_slug(title)
            if slug in used_slugs:
                print(f"  · {md_file.name} → «{title}」已存在，跳过")
                continue
            used_slugs.add(slug)

            tags = list(raw.get("tags", []) or [])
            intro = str(raw.get("intro", "")) or None
            views = int(raw.get("views", 0))
            created_at = _parse_date(raw.get("created_at"))

            # 帖子用固定 UUID（基于文件名 hash）
            post_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, md_file.stem))
            post_sid = make_sid("asse", uuid.UUID(post_id), "post")

            await session.execute(
                text(
                    "INSERT INTO blog_posts "
                    "(id, sid, author_id, title, slug, intro, content, status, "
                    "quality_score, views, required_level, created_at) "
                    "VALUES (:id, :sid, :author_id, :title, :slug, :intro, :content, "
                    "'published', 0, :views, 5, :created_at)"
                ),
                {
                    "id": post_id,
                    "sid": post_sid,
                    "author_id": author_id,
                    "title": title,
                    "slug": slug,
                    "intro": intro,
                    "content": body,
                    "views": views,
                    "created_at": created_at,
                },
            )

            # 标签
            for tag_name in tags:
                normalized = tag_name.strip().lower()
                if not normalized:
                    continue

                tag_row = await session.execute(
                    text("SELECT id FROM blog_tags WHERE LOWER(name) = LOWER(:name)"),
                    {"name": normalized},
                )
                existing_tag = tag_row.scalar()

                if existing_tag:
                    tag_id = existing_tag
                else:
                    tag_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tag:{normalized}"))
                    await session.execute(
                        text(
                            "INSERT OR IGNORE INTO blog_tags (id, name) VALUES (:id, :name)"
                        ),
                        {"id": tag_id, "name": normalized},
                    )
                    created_tags.add(normalized)

                await session.execute(
                    text(
                        "INSERT OR IGNORE INTO blog_post_tags (post_id, tag_id) VALUES (:pid, :tid)"
                    ),
                    {"pid": post_id, "tid": tag_id},
                )

            created_posts += 1
            print(f"  ✓ {md_file.name} → «{title}»")

        await session.commit()
        print(f"\n  完成！帖子: {created_posts}, 标签: {len(created_tags)}")


def main():
    import sys

    reset = "--reset" in sys.argv
    print("博客种子数据写入中...")
    asyncio.run(seed_blog(reset=reset))
    print("OK")


if __name__ == "__main__":
    main()
