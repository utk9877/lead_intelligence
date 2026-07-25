"""Tie each QA review to a specific score (score-grained review gate)

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # qa_reviews is empty (nothing has written reviews yet), so a NOT NULL add is safe.
    op.add_column("qa_reviews", sa.Column("score_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "fk_qa_reviews_score_id_scores", "qa_reviews", "scores", ["score_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_qa_reviews_score_id_scores", "qa_reviews", type_="foreignkey")
    op.drop_column("qa_reviews", "score_id")
