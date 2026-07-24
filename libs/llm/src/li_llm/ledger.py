"""Cost ledger: every LLM call row-logged with account attribution.

The cost-per-account metric (PROJECT_SPEC.md §6) is a query over these rows, not a
spreadsheet. li-llm owns the CostEntry shape and a CostSink protocol; the
Postgres-backed sink lives in li-db, an in-memory sink here serves tests. Stage
values mirror li_db.CostStage so the DB sink maps them 1:1.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable


class CostStage(StrEnum):
    PASS1_TRIGGERS = "pass1_triggers"
    PASS2_RESEARCH = "pass2_research"
    PASS3_SCORING = "pass3_scoring"
    REGISTRY = "registry"
    CRAWL = "crawl"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class CostEntry:
    stage: CostStage
    provider: str
    model: str
    cost_inr: Decimal
    input_tokens: int
    output_tokens: int
    company_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None
    meta: Mapping[str, Any] = field(default_factory=dict)


@runtime_checkable
class CostSink(Protocol):
    def record(self, entry: CostEntry) -> None: ...


class InMemoryCostSink:
    def __init__(self) -> None:
        self.entries: list[CostEntry] = []

    def record(self, entry: CostEntry) -> None:
        self.entries.append(entry)

    def total_inr(self) -> Decimal:
        return sum((e.cost_inr for e in self.entries), Decimal("0"))
