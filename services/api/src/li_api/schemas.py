"""API response/request models (Pydantic). The QA console's read/write contract."""

from __future__ import annotations

import uuid
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class ReviewDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"


class AccountSummary(BaseModel):
    score_id: uuid.UUID
    company_id: uuid.UUID
    customer_id: uuid.UUID
    company_name: str
    value: Decimal
    band: str
    rubric_version: str
    model_version: str


class ReviewRequest(BaseModel):
    company_id: uuid.UUID
    customer_id: uuid.UUID
    reviewer: str
    decision: ReviewDecision
    notes: str | None = None


class ReviewResult(BaseModel):
    id: uuid.UUID
    decision: ReviewDecision


class MergeCandidate(BaseModel):
    id: uuid.UUID
    source: str
    raw_name: str
    candidate_company_id: uuid.UUID | None
    status: str


class CostSummary(BaseModel):
    total_inr: Decimal
    by_stage: dict[str, Decimal]
