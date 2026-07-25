"""Service layer: routers depend on this Protocol, not on the DB directly.

That seam is what makes the routers unit-testable with an in-memory fake (no
Postgres), while DbQaService is the real, DB-backed implementation exercised by
integration tests in CI.
"""

from __future__ import annotations

from typing import Protocol

from li_db.repositories import CostLedgerRepository, QaRepository, ResolutionRepository
from sqlalchemy.orm import Session

from li_api.schemas import (
    AccountSummary,
    CostSummary,
    MergeCandidate,
    ReviewRequest,
    ReviewResult,
)


class QaService(Protocol):
    def review_queue(self) -> list[AccountSummary]: ...
    def record_review(self, request: ReviewRequest) -> ReviewResult: ...
    def merge_queue(self) -> list[MergeCandidate]: ...
    def cost_summary(self) -> CostSummary: ...


class DbQaService:
    """DB-backed QaService. One SQLAlchemy Session per request."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._qa = QaRepository(session)
        self._resolution = ResolutionRepository(session)
        self._cost = CostLedgerRepository(session)

    def review_queue(self) -> list[AccountSummary]:
        return [
            AccountSummary(
                score_id=row.score_id,
                company_id=row.company_id,
                customer_id=row.customer_id,
                company_name=row.company_name,
                value=row.value,
                band=row.band.value,
                rubric_version=row.rubric_version,
                model_version=row.model_version,
            )
            for row in self._qa.review_queue()
        ]

    def record_review(self, request: ReviewRequest) -> ReviewResult:
        review = self._qa.record_review(
            score_id=request.score_id,
            company_id=request.company_id,
            customer_id=request.customer_id,
            reviewer=request.reviewer,
            decision=request.decision.value,
            notes=request.notes,
        )
        self._session.commit()
        return ReviewResult(id=review.id, decision=request.decision)

    def merge_queue(self) -> list[MergeCandidate]:
        return [
            MergeCandidate(
                id=candidate.id,
                source=candidate.source,
                raw_name=candidate.raw_name,
                candidate_company_id=candidate.candidate_company_id,
                status=candidate.status.value,
            )
            for candidate in self._resolution.pending()
        ]

    def cost_summary(self) -> CostSummary:
        return CostSummary(total_inr=self._cost.total_inr(), by_stage=self._cost.by_stage())
