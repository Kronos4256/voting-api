"""create voting tables

Revision ID: 0001
Revises:
Create Date: 2026-11-19 12:12:50
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("party", sa.String(length=120), nullable=True),
        sa.Column("votes", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("votes >= 0", name=op.f("ck_candidates_votes_non_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_candidates")),
        sa.UniqueConstraint("email", name=op.f("uq_candidates_email")),
    )
    op.create_table(
        "voters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("has_voted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_voters")),
        sa.UniqueConstraint("email", name=op.f("uq_voters_email")),
    )
    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("voter_id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["candidate_id"], ["candidates.id"], name=op.f("fk_votes_candidate_id_candidates")
        ),
        sa.ForeignKeyConstraint(["voter_id"], ["voters.id"], name=op.f("fk_votes_voter_id_voters")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_votes")),
        sa.UniqueConstraint("voter_id", name=op.f("uq_votes_voter_id")),
    )
    op.create_index(op.f("ix_votes_candidate_id"), "votes", ["candidate_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_votes_candidate_id"), table_name="votes")
    op.drop_table("votes")
    op.drop_table("voters")
    op.drop_table("candidates")
