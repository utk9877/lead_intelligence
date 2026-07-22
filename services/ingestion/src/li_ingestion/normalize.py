"""Normalization helpers: build candidate signals that are company-level by construction.

Every candidate signal's payload passes `assert_company_level` at build time, so a
person-shaped field can never reach the graph — a violation raises here, at the
ingest boundary, rather than being written and cleaned up later (ADR-005).
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from li_compliance.guards import assert_company_level
from li_core.models import SignalType

from li_ingestion.artifacts import CandidateSignal


def build_signal(
    *,
    signal_type: SignalType,
    observed_at: datetime,
    payload: Mapping[str, object],
    context: str,
) -> CandidateSignal:
    assert_company_level(payload, context=context)
    return CandidateSignal(type=signal_type, observed_at=observed_at, payload=dict(payload))


def posting_summary(roles: list[str], open_count: int) -> dict[str, object]:
    """Hiring signal at the POSTING level only — counts and role titles, never
    candidate/recruiter person data (ADR-005; careers/job-board adapters)."""
    return {"open_postings": open_count, "roles": sorted(set(roles))}
