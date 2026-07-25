"""Repository for the human QA gate: the review queue and review recording.

The review queue is every scored (company, customer) pair that has NOT yet been
reviewed — a left-anti-join of scores against qa_reviews. Recording a review is an
append to the append-only qa_reviews table.
"""

import uuid
from dataclasses import dataclass
from decimal import Decimal

from li_core.models import ScoreBand
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from li_db.orm import Company, QaDecision, QaReview, Score


@dataclass(frozen=True, slots=True)
class ReviewableAccount:
    score_id: uuid.UUID
    company_id: uuid.UUID
    customer_id: uuid.UUID
    company_name: str
    value: Decimal
    band: ScoreBand
    rubric_version: str
    model_version: str


class QaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _reviewed_scores(self) -> Select[tuple[uuid.UUID]]:
        return select(QaReview.score_id)

    def review_queue(self) -> list[ReviewableAccount]:
        # Score-grained: a score is in the queue until THAT score has a review, so a
        # re-scored account re-enters the gate rather than inheriting an old verdict.
        stmt = (
            select(Score, Company.name)
            .join(Company, Score.company_id == Company.id)
            .where(Score.id.not_in(self._reviewed_scores()))
            .order_by(Score.value.desc())
        )
        return [
            ReviewableAccount(
                score_id=score.id,
                company_id=score.company_id,
                customer_id=score.customer_id,
                company_name=name,
                value=score.value,
                band=score.band,
                rubric_version=score.rubric_version,
                model_version=score.model_version,
            )
            for score, name in self._session.execute(stmt).all()
        ]

    def record_review(
        self,
        *,
        score_id: uuid.UUID,
        company_id: uuid.UUID,
        customer_id: uuid.UUID,
        reviewer: str,
        decision: QaDecision | str,
        notes: str | None = None,
    ) -> QaReview:
        review = QaReview(
            score_id=score_id,
            company_id=company_id,
            customer_id=customer_id,
            reviewer=reviewer,
            decision=QaDecision(decision),
            notes=notes,
        )
        self._session.add(review)
        self._session.flush()
        return review
