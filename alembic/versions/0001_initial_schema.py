"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-21 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = "8a28f0ff45c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="farmer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # crops table
    op.create_table(
        "crops",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("season", sa.String(100), nullable=True),
        sa.Column("common_diseases", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crops_name", "crops", ["name"], unique=True)

    # disease_scans table
    op.create_table(
        "disease_scans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("crop_name", sa.String(100), nullable=False),
        sa.Column("predicted_disease", sa.String(200), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("treatment_advice", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_disease_scans_user_id", "disease_scans", ["user_id"])

    # disease_knowledge table with pgvector column
    op.create_table(
        "disease_knowledge",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("disease_name", sa.String(200), nullable=False),
        sa.Column("crop_name", sa.String(100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(500), nullable=True),
        sa.Column("embedding", sa.Text(), nullable=True),  # placeholder, overridden below
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Drop the placeholder embedding column and add real vector column
    op.drop_column("disease_knowledge", "embedding")
    op.execute("ALTER TABLE disease_knowledge ADD COLUMN embedding vector(768)")
    op.create_index("ix_disease_knowledge_disease_name", "disease_knowledge", ["disease_name"])
    op.create_index("ix_disease_knowledge_crop_name", "disease_knowledge", ["crop_name"])


def downgrade() -> None:
    op.drop_table("disease_knowledge")
    op.drop_table("disease_scans")
    op.drop_table("crops")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
