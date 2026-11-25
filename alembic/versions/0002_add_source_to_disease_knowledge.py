"""add source column to disease_knowledge

Revision ID: 0002
Revises: 3a2d31b2475c
Create Date: 2026-11-23 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "3a2d31b2475c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "disease_knowledge",
        sa.Column("source", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("disease_knowledge", "source")
