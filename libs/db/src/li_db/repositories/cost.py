"""Repository for the cost ledger — cost-per-account is a query over these rows."""

import uuid
from collections.abc import Mapping
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from li_db.orm import CostLedgerEntry, CostStage


class CostLedgerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        *,
        stage: CostStage | str,
        provider: str,
        cost_inr: Decimal,
        model: str | None = None,
        company_id: uuid.UUID | None = None,
        customer_id: uuid.UUID | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        meta: Mapping[str, Any] | None = None,
    ) -> CostLedgerEntry:
        entry = CostLedgerEntry(
            stage=CostStage(stage),
            provider=provider,
            model=model,
            cost_inr=cost_inr,
            company_id=company_id,
            customer_id=customer_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            meta=dict(meta or {}),
        )
        self._session.add(entry)
        self._session.flush()
        return entry

    def total_inr(self, *, customer_id: uuid.UUID | None = None) -> Decimal:
        stmt = select(func.coalesce(func.sum(CostLedgerEntry.cost_inr), 0))
        if customer_id is not None:
            stmt = stmt.where(CostLedgerEntry.customer_id == customer_id)
        return self._session.scalar(stmt) or Decimal("0")
