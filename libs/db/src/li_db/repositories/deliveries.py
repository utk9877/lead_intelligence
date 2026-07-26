"""Repository for deliveries + customer feedback (the labelled data).

A delivery links a QA-approved score to a customer; feedback (pursue/reject) is set
later when the customer responds — that pursue/reject is the label the precision
metric and future scoring learn from (PROJECT_SPEC.md §6).
"""

import uuid
from datetime import UTC, datetime

from li_core.errors import LeadIntelligenceError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from li_db.orm import Delivery, DeliveryFeedback


class FeedbackAlreadyRecordedError(LeadIntelligenceError):
    """Feedback for this delivery was already recorded; it is set-once (the label
    is audit data — a changed verdict is a new signal, not a silent overwrite)."""


class DeliveryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def record_delivery(
        self,
        *,
        customer_id: uuid.UUID,
        company_id: uuid.UUID,
        score_id: uuid.UUID,
        qa_review_id: uuid.UUID,
    ) -> Delivery:
        delivery = Delivery(
            customer_id=customer_id,
            company_id=company_id,
            score_id=score_id,
            qa_review_id=qa_review_id,
        )
        self._session.add(delivery)
        self._session.flush()
        return delivery

    def record_feedback(
        self,
        delivery_id: uuid.UUID,
        feedback: DeliveryFeedback | str,
        *,
        at: datetime | None = None,
    ) -> Delivery:
        delivery = self._session.get(Delivery, delivery_id)
        if delivery is None:
            raise KeyError(f"no delivery {delivery_id}")
        if delivery.feedback is not None:
            # Set-once: never silently overwrite a recorded verdict (audit integrity).
            raise FeedbackAlreadyRecordedError(
                f"delivery {delivery_id} already has feedback {delivery.feedback.value}"
            )
        delivery.feedback = DeliveryFeedback(feedback)
        delivery.feedback_at = at or datetime.now(UTC)
        self._session.flush()
        return delivery

    def with_feedback(self) -> list[Delivery]:
        return list(
            self._session.scalars(select(Delivery).where(Delivery.feedback.is_not(None))).all()
        )

    def count(self) -> int:
        return self._session.scalar(select(func.count()).select_from(Delivery)) or 0
