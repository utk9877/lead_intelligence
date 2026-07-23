"""Resolver orchestrator: candidate → Resolution.

Order: hard anchor (CIN/GSTIN) first; if that yields a company, we're done. A
conflict or an unanchored candidate goes to the merge queue with the best fallback
hint attached. Auto-creation only ever happens from a registry identifier, so the
graph never grows an un-dedupable company automatically.
"""

from __future__ import annotations

from li_core.models import CandidateCompany
from li_db.repositories import CompanyRepository, ResolutionRepository

from li_resolver.anchor import AnchorConflict, AnchorMatch, anchor_resolve
from li_resolver.fallback import fallback_hint
from li_resolver.outcomes import Disposition, Resolution, ResolutionMethod


def resolve(
    candidate: CandidateCompany,
    companies: CompanyRepository,
    queue: ResolutionRepository,
    *,
    source: str,
) -> Resolution:
    outcome = anchor_resolve(candidate, companies)

    if isinstance(outcome, AnchorMatch):
        if outcome.created:
            return Resolution(
                disposition=Disposition.CREATED,
                method=ResolutionMethod.CREATED_ANCHORED,
                company_id=outcome.company.id,
                reason="created, anchored on CIN/GSTIN",
            )
        return Resolution(
            disposition=Disposition.MATCHED,
            method=ResolutionMethod.CIN if candidate.cin else ResolutionMethod.GSTIN,
            company_id=outcome.company.id,
            reason=f"matched on {'CIN' if candidate.cin else 'GSTIN'}",
        )

    if isinstance(outcome, AnchorConflict):
        queue.enqueue(
            source=source,
            raw_name=candidate.name,
            payload=_candidate_payload(candidate),
            candidate_company_id=outcome.hint_company_id,
        )
        return Resolution(
            disposition=Disposition.QUEUED,
            method=outcome.method,
            company_id=None,
            reason=outcome.reason,
        )

    # Unanchored: queue with the best fallback hint (a probable company for a human).
    hint = fallback_hint(candidate, companies)
    queue.enqueue(
        source=source,
        raw_name=candidate.name,
        payload=_candidate_payload(candidate),
        candidate_company_id=hint.company_id,
    )
    return Resolution(
        disposition=Disposition.QUEUED,
        method=hint.method,
        company_id=None,  # not resolved; a human confirms the hinted company
        reason=hint.reason,
    )


def _candidate_payload(candidate: CandidateCompany) -> dict[str, object]:
    return {
        "name": candidate.name,
        "cin": candidate.cin,
        "gstin": candidate.gstin,
        "domain": candidate.domain,
    }
