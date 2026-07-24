"""Repository for the human merge queue (resolution_candidates)."""

import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from li_db.orm import ResolutionCandidate, ResolutionStatus


class ResolutionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def enqueue(
        self,
        *,
        source: str,
        raw_name: str,
        payload: Mapping[str, Any],
        candidate_company_id: uuid.UUID | None = None,
    ) -> ResolutionCandidate:
        candidate = ResolutionCandidate(
            source=source,
            raw_name=raw_name,
            payload=dict(payload),
            candidate_company_id=candidate_company_id,
            status=ResolutionStatus.PENDING,
        )
        self._session.add(candidate)
        self._session.flush()
        return candidate

    def pending(self) -> list[ResolutionCandidate]:
        return list(
            self._session.scalars(
                select(ResolutionCandidate).where(
                    ResolutionCandidate.status == ResolutionStatus.PENDING
                )
            ).all()
        )
