"""initial_users_papers

Revision ID: 32761cfdd694
Revises:
Create Date: 2026-04-11

既存の旧スキーマ（HTMX版）を廃棄し、多ユーザー対応の新スキーマを初期作成する。
既存データを移行する場合は scripts/migrate_legacy.py を参照。
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "32761cfdd694"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 旧テーブルを削除（存在する場合）
    op.execute("DROP TABLE IF EXISTS schema_version")
    op.execute("DROP TABLE IF EXISTS papers")

    # users テーブル新規作成
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # papers テーブル新規作成
    op.create_table(
        "papers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("authors", sa.Text(), nullable=False, server_default=""),
        sa.Column("url", sa.Text(), nullable=False, server_default=""),
        sa.Column("memo", sa.Text(), nullable=False, server_default=""),
        sa.Column("tags", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_papers_user_id"), "papers", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_papers_user_id"), table_name="papers")
    op.drop_table("papers")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
