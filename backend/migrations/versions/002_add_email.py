"""add email to users

Revision ID: 002_add_email
Revises: 001_initial
Create Date: 2026-04-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "002_add_email"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 添加列
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(128), nullable=True))

    # 2. 为现有行设置默认值（batch 外执行 DML）
    op.execute("UPDATE users SET email = username || '@local' WHERE email IS NULL")

    # 3. 设为 NOT NULL 并创建唯一约束
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("email", nullable=False)
        batch_op.create_unique_constraint("uq_users_email", ["email"])


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_email", type_="unique")
        batch_op.drop_column("email")
