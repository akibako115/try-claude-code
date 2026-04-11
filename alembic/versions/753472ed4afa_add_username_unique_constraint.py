"""add_username_unique_constraint

Revision ID: 753472ed4afa
Revises: 32761cfdd694
Create Date: 2026-04-11

"""
from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "753472ed4afa"
down_revision: str | None = "32761cfdd694"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.create_unique_constraint("uq_users_username", ["username"])


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_username", type_="unique")
