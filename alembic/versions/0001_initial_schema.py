"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "opportunities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("niche_title", sa.String(length=255), nullable=False),
        sa.Column("niche_description", sa.Text(), nullable=False, server_default=""),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="other"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="discovered"),
        sa.Column("exported", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("claimed_at", sa.DateTime(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("opportunities")
