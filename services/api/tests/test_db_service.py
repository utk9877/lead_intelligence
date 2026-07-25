"""DbQaService against a real Postgres schema (runs in CI; skips locally)."""

from __future__ import annotations

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


def _seed_scored_account(session: Session) -> Score:
    company = CompanyRepository(session).add(name="Fictional Widgets Pvt Ltd", cin=CIN)
    customer = Customer(name="DevOps SaaS Co", niche="funded SMBs")
    session.add(customer)
    session.flush()
    score = Score(
        company_id=company.id,
        customer_id=customer.id,
        value=Decimal("80.00"),
        band="warm",
        rubric_version="r1",
        model_version="claude-sonnet-5",
    )
    session.add(score)
    session.flush()
    return score


def test_review_queue_then_review_removes_from_queue(db_session: Session) -> None:
    score = _seed_scored_account(db_session)
    service = DbQaService(db_session)

    queue = service.review_queue()
    assert [a.score_id for a in queue] == [score.id]

    service.record_review(
        ReviewRequest(
            score_id=score.id,
            company_id=score.company_id,
            customer_id=score.customer_id,
            reviewer="alice",
            decision=ReviewDecision.APPROVE,
        )
    )
    # Once THAT score is reviewed, it leaves the queue.
    assert service.review_queue() == []


def test_rescore_reenters_the_review_queue(db_session: Session) -> None:
    score = _seed_scored_account(db_session)
    service = DbQaService(db_session)
    service.record_review(
        ReviewRequest(
            score_id=score.id,
            company_id=score.company_id,
            customer_id=score.customer_id,
            reviewer="alice",
            decision=ReviewDecision.APPROVE,
        )
    )
    assert service.review_queue() == []
    # A NEW score for the same company/customer must NOT inherit the old verdict.
    rescored = Score(
        company_id=score.company_id,
        customer_id=score.customer_id,
        value=Decimal("90.00"),
        band="hot",
        rubric_version="r1",
        model_version="claude-opus-4-8",
    )
    db_session.add(rescored)
    db_session.flush()
    assert [a.score_id for a in service.review_queue()] == [rescored.id]


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
