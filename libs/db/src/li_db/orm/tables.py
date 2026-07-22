"""The company graph + ops tables (docs/ARCHITECTURE.md §3).

Hard rules encoded structurally:
- No person-level columns, ever (ADR-005) — tests/test_schema_policy.py scans this
  metadata and CI fails if a person-shaped column appears.
- A signal always cites evidence (`signals.evidence_id` NOT NULL).
- Nothing is delivered without QA (`deliveries.qa_review_id` NOT NULL).
- `qa_reviews` and `deliveries` are append-only (no updated_at; API layer only inserts).
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from li_core.models import ScoreBand, SignalType
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from li_db.orm.base import Base


def _enum(enum_class: type[enum.Enum], name: str) -> SAEnum:
    return SAEnum(enum_class, name=name, values_callable=lambda e: [member.value for member in e])


class IdentifierKind(enum.StrEnum):
    CIN = "cin"
    GSTIN = "gstin"
    DOMAIN = "domain"
    MARKETPLACE = "marketplace"


class QaDecision(enum.StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"


class DeliveryFeedback(enum.StrEnum):
    PURSUE = "pursue"
    REJECT = "reject"


class ResolutionStatus(enum.StrEnum):
    PENDING = "pending"
    MERGED = "merged"
    DISMISSED = "dismissed"


class CostStage(enum.StrEnum):
    PASS1_TRIGGERS = "pass1_triggers"
    PASS2_RESEARCH = "pass2_research"
    PASS3_SCORING = "pass3_scoring"
    REGISTRY = "registry"
    CRAWL = "crawl"
    OTHER = "other"


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        Index(
            "uq_companies_cin",
            "cin",
            unique=True,
            postgresql_where=text("cin IS NOT NULL"),
        ),
        Index(
            "uq_companies_gstin",
            "gstin",
            unique=True,
            postgresql_where=text("gstin IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text)
    cin: Mapped[str | None] = mapped_column(String(21))
    gstin: Mapped[str | None] = mapped_column(String(15))
    domain: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CompanyIdentifier(Base):
    __tablename__ = "company_identifiers"
    __table_args__ = (UniqueConstraint("kind", "value"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    kind: Mapped[IdentifierKind] = mapped_column(_enum(IdentifierKind, "identifier_kind"))
    value: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_url: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True)
    snapshot_key: Mapped[str] = mapped_column(Text)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (Index("ix_signals_company_type", "company_id", "type"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    type: Mapped[SignalType] = mapped_column(_enum(SignalType, "signal_type"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text)
    niche: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (Index("ix_scores_customer_company", "customer_id", "company_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    value: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    band: Mapped[ScoreBand] = mapped_column(_enum(ScoreBand, "score_band"))
    rubric_version: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class QaReview(Base):
    __tablename__ = "qa_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"))
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"))
    reviewer: Mapped[str] = mapped_column(Text)
    decision: Mapped[QaDecision] = mapped_column(_enum(QaDecision, "qa_decision"))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"))
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"))
    score_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scores.id"))
    qa_review_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("qa_reviews.id"))
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    feedback: Mapped[DeliveryFeedback | None] = mapped_column(
        _enum(DeliveryFeedback, "delivery_feedback")
    )
    feedback_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ResolutionCandidate(Base):
    __tablename__ = "resolution_candidates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(Text)
    raw_name: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    candidate_company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL")
    )
    status: Mapped[ResolutionStatus] = mapped_column(
        _enum(ResolutionStatus, "resolution_status"), default=ResolutionStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CostLedgerEntry(Base):
    __tablename__ = "cost_ledger"
    __table_args__ = (
        Index("ix_cost_ledger_occurred_at", "occurred_at"),
        Index("ix_cost_ledger_customer", "customer_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    stage: Mapped[CostStage] = mapped_column(_enum(CostStage, "cost_stage"))
    provider: Mapped[str] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(Text)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL")
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL")
    )
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_inr: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    meta: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
