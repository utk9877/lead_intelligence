"""Resolver orchestrator: candidate → Resolution.

Order: hard anchor (CIN/GSTIN) first; if that yields a company, we're done. A
conflict or an unanchored candidate goes to the merge queue with the best fallback
hint attached. Auto-creation only ever happens from a registry identifier, so the
graph never grows an un-dedupable company automatically.

A structurally-invalid CIN/GSTIN raises InvalidIdentifierError out of normalize_ids
rather than being silently accepted — resolve() is intentionally not total. Today
only the registry adapters populate identifiers and they pre-validate, so no live
producer can feed a malformed one; when the worker loop is wired it will dead-letter
such records rather than abort the batch.
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
        # A duplicate discovered while enriching (same PAN, different company) is
        # surfaced for human merge; the candidate itself still resolved correctly.
        if outcome.pan_merge_hint is not None:
            queue.enqueue(
                source=source,
                raw_name=candidate.name,
                payload=_candidate_payload(candidate),
                candidate_company_id=outcome.pan_merge_hint,
            )
        method = outcome.matched_on or ResolutionMethod.CIN
        return Resolution(
            disposition=Disposition.MATCHED,
            method=method,
            company_id=outcome.company.id,
            reason=f"matched on {method.value.upper()}",
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
