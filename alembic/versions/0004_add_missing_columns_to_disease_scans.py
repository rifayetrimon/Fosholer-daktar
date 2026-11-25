"""add confidence, treatment_advice, notes to disease_scans

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-24 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("disease_scans", sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"))
    op.add_column("disease_scans", sa.Column("treatment_advice", sa.Text(), nullable=True))
    op.add_column("disease_scans", sa.Column("notes", sa.Text(), nullable=True))
    # Remove the default constraint after backfill so future inserts must supply a value
    op.alter_column("disease_scans", "confidence", server_default=None)


def downgrade() -> None:
    op.drop_column("disease_scans", "notes")
    op.drop_column("disease_scans", "treatment_advice")
    op.drop_column("disease_scans", "confidence")
