"""Account-level value types for the three-pass pipeline.

Company-level only (ADR-005). Every Claim and TriggerFinding carries the id of the
evidence that backs it — the pipeline refuses to emit an uncited claim.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field

from li_core.models import ScoreBand, SignalType


@dataclass(frozen=True, slots=True)
class Observation:
    """A fact snippet handed to pass 1, with the evidence that supports it."""

    text: str
    evidence_id: uuid.UUID


@dataclass(frozen=True, slots=True)
class CompanyFacts:
    company_id: uuid.UUID
    name: str
    observations: Sequence[Observation]
    cin: str | None = None
    gstin: str | None = None
    domain: str | None = None


@dataclass(frozen=True, slots=True)
class CustomerICP:
    """The stable per-customer preamble — the cacheable prompt prefix."""

    customer_id: uuid.UUID
    offering: str
    niche: str


@dataclass(frozen=True, slots=True)
class TriggerFinding:
    type: SignalType
    confidence: float
    evidence_id: uuid.UUID


@dataclass(frozen=True, slots=True)
class Claim:
    text: str
    evidence_id: uuid.UUID


@dataclass(frozen=True, slots=True)
class ResearchedAccount:
    company_id: uuid.UUID
    why_now: str
    why_fit: str
    claims: Sequence[Claim] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class AccountScore:
    value: float
    band: ScoreBand
    rubric_version: str
    model_version: str
    rationale: str
