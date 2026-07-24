"""Fallback hints for UNANCHORED candidates (no CIN, no GSTIN).

These never auto-match; they only produce a *hint* (a probable company) that
accompanies the merge-queue entry, so a human starts from the best guess. Domain
is not unique (parent/subsidiary share sites), so even a single domain match is a
human decision, not an automatic merge (QUESTIONS.md#entity-resolution). PAN-based
hints are handled earlier in the anchored path, since they require a GSTIN.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from li_core.models import CandidateCompany
from li_db.repositories import CompanyRepository

from li_resolver.outcomes import ResolutionMethod


@dataclass(frozen=True, slots=True)
class FallbackHint:
    method: ResolutionMethod
    company_id: uuid.UUID | None
    reason: str


def fallback_hint(candidate: CandidateCompany, companies: CompanyRepository) -> FallbackHint:
    if candidate.domain:
        hits = companies.get_by_domain(candidate.domain)
        if len(hits) == 1:
            return FallbackHint(
                method=ResolutionMethod.DOMAIN_HINT,
                company_id=hits[0].id,
                reason=f"single domain match on {candidate.domain}",
            )
        if len(hits) > 1:
            return FallbackHint(
                method=ResolutionMethod.AMBIGUOUS_DOMAIN,
                company_id=None,
                reason=f"{len(hits)} companies share domain {candidate.domain}",
            )

    return FallbackHint(
        method=ResolutionMethod.NAME_ONLY,
        company_id=None,
        reason="no CIN/GSTIN/domain match; name alone is too weak to auto-resolve",
    )
