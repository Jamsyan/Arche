"""add sid (Searchable ID) columns to all models

Revision ID: 011_add_sid
Revises: 010_add_user_soft_delete_fields
Create Date: 2026-06-07 12:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "011_add_sid"
down_revision: Union[str, None] = "010_add_user_soft_delete_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── 所有需要加 sid 的表 ──
_TABLES = [
    "users",
    "blog_posts",
    "blog_comments",
    "blog_likes",
    "blog_reports",
    "blog_tags",
    "blog_favorites",
    "blog_post_files",
    "oss_files",
    "user_oss_quotas",
    "asset_index",
    "training_jobs",
    "training_instances",
    "training_costs",
    "training_task_steps",
    "datasets",
    "code_repos",
    "artifacts",
    "crawl_records",
    "monitor_templates",
]


def upgrade() -> None:
    for table_name in _TABLES:
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            batch_op.add_column(
                sa.Column(
                    "sid",
                    sa.String(length=64),
                    nullable=False,
                    server_default="",
                )
            )
            batch_op.create_index(
                f"ix_{table_name}_sid", ["sid"], unique=True
            )


def downgrade() -> None:
    for table_name in _TABLES:
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            batch_op.drop_index(f"ix_{table_name}_sid")
            batch_op.drop_column("sid")
