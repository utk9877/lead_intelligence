"""Initial company graph + ops tables

Revision ID: 0001
Revises:
Create Date: 2026-07-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

identifier_kind = sa.Enum("cin", "gstin", "domain", "marketplace", name="identifier_kind")
signal_type = sa.Enum(
    "funding_round",
    "hiring_surge",
    "new_incorporation",
    "gst_registration",
    "expansion",
    "tech_adoption",
    name="signal_type",
)
score_band = sa.Enum("hot", "warm", "not_warm", name="score_band")
qa_decision = sa.Enum("approve", "reject", "edit", name="qa_decision")
delivery_feedback = sa.Enum("pursue", "reject", name="delivery_feedback")
resolution_status = sa.Enum("pending", "merged", "dismissed", name="resolution_status")
cost_stage = sa.Enum(
    "pass1_triggers",
    "pass2_research",
    "pass3_scoring",
    "registry",
    "crawl",
    "other",
    name="cost_stage",
)


def upgrade() -> None:
    # Embeddings (chunk 4) live in this database; establish the extension now.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("cin", sa.String(length=21), nullable=True),
        sa.Column("gstin", sa.String(length=15), nullable=True),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_companies"),
    )
    op.create_index(
        "uq_companies_cin",
        "companies",
        ["cin"],
        unique=True,
        postgresql_where=sa.text("cin IS NOT NULL"),
    )
    op.create_index(
        "uq_companies_gstin",
        "companies",
        ["gstin"],
        unique=True,
        postgresql_where=sa.text("gstin IS NOT NULL"),
    )

    op.create_table(
        "company_identifiers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("kind", identifier_kind, nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_company_identifiers"),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_company_identifiers_company_id_companies",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("kind", "value", name="uq_company_identifiers_kind"),
    )

    op.create_table(
        "evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("snapshot_key", sa.Text(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_evidence"),
        sa.UniqueConstraint("content_hash", name="uq_evidence_content_hash"),
    )

    op.create_table(
        "signals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("type", signal_type, nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_signals"),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_signals_company_id_companies",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id"], ["evidence.id"], name="fk_signals_evidence_id_evidence"
        ),
    )
    op.create_index("ix_signals_company_type", "signals", ["company_id", "type"])

    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("niche", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_customers"),
    )

    op.create_table(
        "scores",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("value", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("band", score_band, nullable=False),
        sa.Column("rubric_version", sa.Text(), nullable=False),
        sa.Column("model_version", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_scores"),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_scores_company_id_companies",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_scores_customer_id_customers",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_scores_customer_company", "scores", ["customer_id", "company_id"])

    op.create_table(
        "qa_reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("reviewer", sa.Text(), nullable=False),
        sa.Column("decision", qa_decision, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_qa_reviews"),
        sa.ForeignKeyConstraint(
            ["company_id"], ["companies.id"], name="fk_qa_reviews_company_id_companies"
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["customers.id"], name="fk_qa_reviews_customer_id_customers"
        ),
    )

    op.create_table(
        "deliveries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("score_id", sa.Uuid(), nullable=False),
        sa.Column("qa_review_id", sa.Uuid(), nullable=False),
        sa.Column(
            "delivered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("feedback", delivery_feedback, nullable=True),
        sa.Column("feedback_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_deliveries"),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["customers.id"], name="fk_deliveries_customer_id_customers"
        ),
        sa.ForeignKeyConstraint(
            ["company_id"], ["companies.id"], name="fk_deliveries_company_id_companies"
        ),
        sa.ForeignKeyConstraint(["score_id"], ["scores.id"], name="fk_deliveries_score_id_scores"),
        sa.ForeignKeyConstraint(
            ["qa_review_id"],
            ["qa_reviews.id"],
            name="fk_deliveries_qa_review_id_qa_reviews",
        ),
    )

    op.create_table(
        "resolution_candidates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("raw_name", sa.Text(), nullable=False),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column("candidate_company_id", sa.Uuid(), nullable=True),
        sa.Column("status", resolution_status, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_resolution_candidates"),
        sa.ForeignKeyConstraint(
            ["candidate_company_id"],
            ["companies.id"],
            name="fk_resolution_candidates_candidate_company_id_companies",
            ondelete="SET NULL",
        ),
    )

    op.create_table(
        "cost_ledger",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("stage", cost_stage, nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("model", sa.Text(), nullable=True),
        sa.Column("company_id", sa.Uuid(), nullable=True),
        sa.Column("customer_id", sa.Uuid(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("cost_inr", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("meta", JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_cost_ledger"),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_cost_ledger_company_id_companies",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_cost_ledger_customer_id_customers",
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_cost_ledger_occurred_at", "cost_ledger", ["occurred_at"])
    op.create_index("ix_cost_ledger_customer", "cost_ledger", ["customer_id"])


def downgrade() -> None:
    op.drop_table("cost_ledger")
    op.drop_table("resolution_candidates")
    op.drop_table("deliveries")
    op.drop_table("qa_reviews")
    op.drop_table("scores")
    op.drop_table("customers")
    op.drop_table("signals")
    op.drop_table("evidence")
    op.drop_table("company_identifiers")
    op.drop_table("companies")
    bind = op.get_bind()
    for enum_type in (
        cost_stage,
        resolution_status,
        delivery_feedback,
        qa_decision,
        score_band,
        signal_type,
        identifier_kind,
    ):
        enum_type.drop(bind, checkfirst=True)
