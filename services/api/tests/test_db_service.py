"""DbQaService against a real Postgres schema (runs in CI; skips locally)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from li_api.schemas import ReviewDecision, ReviewRequest
from li_api.service import DbQaService
from li_db.orm import Customer, Score
from li_db.repositories import CompanyRepository, CostLedgerRepository
from li_db.testing import database_url
from sqlalchemy.orm import Session

pytestmark = pytest.mark.skipif(
    database_url() is None, reason="DATABASE_URL not set (Postgres integration tests)"
)

CIN = "U12345MH2019PTC123456"


def _seed_scored_account(session: Session) -> tuple[uuid.UUID, uuid.UUID]:
    company = CompanyRepository(session).add(name="Fictional Widgets Pvt Ltd", cin=CIN)
    customer = Customer(name="DevOps SaaS Co", niche="funded SMBs")
    session.add(customer)
    session.flush()
    session.add(
        Score(
            company_id=company.id,
            customer_id=customer.id,
            value=Decimal("80.00"),
            band="warm",
            rubric_version="r1",
            model_version="claude-sonnet-5",
        )
    )
    session.flush()
    return company.id, customer.id


def test_review_queue_then_review_removes_from_queue(db_session: Session) -> None:
    company_id, customer_id = _seed_scored_account(db_session)
    service = DbQaService(db_session)

    queue = service.review_queue()
    assert [a.company_id for a in queue] == [company_id]

    service.record_review(
        ReviewRequest(
            company_id=company_id,
            customer_id=customer_id,
            reviewer="alice",
            decision=ReviewDecision.APPROVE,
        )
    )
    # Once reviewed, the account leaves the queue (left-anti-join).
    assert service.review_queue() == []


def test_cost_summary_rolls_up_by_stage(db_session: Session) -> None:
    CostLedgerRepository(db_session).add(
        stage="pass1_triggers", provider="anthropic", cost_inr=Decimal("83.00")
    )
    CostLedgerRepository(db_session).add(
        stage="pass2_research", provider="anthropic", cost_inr=Decimal("166.00")
    )
    summary = DbQaService(db_session).cost_summary()
    assert summary.total_inr == Decimal("249.00")
    assert summary.by_stage["pass1_triggers"] == Decimal("83.00")
