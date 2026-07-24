"""Hard-anchor resolution on CIN/GSTIN (ADR-001).

Only candidates carrying a registry identifier are auto-resolved or auto-created
here. That keeps the auto-created population deduplicated by identifier: the
mismatch rate is zero (we never merge two different anchored companies) and the
duplicate rate is driven only by missing cross-identifiers, which `enrich` repairs.

Unanchored candidates are never created here — they go to the merge queue
(fallback.py), because a name or a shared domain is not strong enough to create or
merge a company without human confirmation (QUESTIONS.md#entity-resolution).

**Trust boundary.** The zero-mismatch guarantee assumes each candidate is
*internally consistent* — its CIN and GSTIN belong to the same company. This holds
because a candidate is built from a single source record (an MCA record pairs a
company's CIN with its own GSTINs). If a source ever emitted a CIN and GSTIN from
two different companies in one record, enrichment could attach the wrong GSTIN;
that is a source-data defect, not a resolver behaviour, and is out of scope here.
Cross-identifier *conflicts we can observe* (both ids already pointing at two
different companies) are still caught below and queued, never merged.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from li_core.ids import parse_cin, parse_gstin
from li_core.models import CandidateCompany
from li_db.orm import Company
from li_db.repositories import CompanyRepository

from li_resolver.outcomes import ResolutionMethod


@dataclass(frozen=True, slots=True)
class AnchorMatch:
    company: Company
    created: bool  # True if a new company was created, False if an existing one matched
    matched_on: ResolutionMethod | None = None  # which identifier matched (None if created)
    # If, while enriching, we discover the matched company shares a PAN with a
    # *different* company, that is a duplicate to surface for human merge — set here.
    pan_merge_hint: uuid.UUID | None = None


@dataclass(frozen=True, slots=True)
class AnchorConflict:
    """The anchored candidate cannot be auto-resolved and must be queued: either its
    two identifiers point at different companies (IDENTIFIER_CONFLICT), an identifier
    disagrees with the matched company's own, or its GSTIN shares a PAN with an
    existing company (PAN_MATCH — same legal entity, different state registration)."""

    method: ResolutionMethod
    reason: str
    hint_company_id: uuid.UUID | None = None


def normalize_ids(candidate: CandidateCompany) -> tuple[str | None, str | None]:
    cin = parse_cin(candidate.cin).normalized if candidate.cin else None
    gstin = parse_gstin(candidate.gstin).normalized if candidate.gstin else None
    return cin, gstin


def anchor_resolve(
    candidate: CandidateCompany, companies: CompanyRepository
) -> AnchorMatch | AnchorConflict | None:
    """Return an AnchorMatch (matched or created), an AnchorConflict to queue, or
    None when the candidate is unanchored (caller falls back to the merge queue)."""
    cin, gstin = normalize_ids(candidate)
    if cin is None and gstin is None:
        return None

    cin_match = companies.get_by_cin(cin) if cin else None
    gstin_match = companies.get_by_gstin(gstin) if gstin else None

    if cin_match and gstin_match and cin_match.id != gstin_match.id:
        return AnchorConflict(
            method=ResolutionMethod.IDENTIFIER_CONFLICT,
            reason=f"CIN {cin} matches {cin_match.id} but GSTIN {gstin} matches {gstin_match.id}",
        )

    matched = cin_match or gstin_match
    if matched is not None:
        # A present-but-different identifier on the matched company is a conflict.
        if cin and matched.cin and matched.cin != cin:
            return AnchorConflict(
                method=ResolutionMethod.IDENTIFIER_CONFLICT,
                reason=f"matched {matched.id} has CIN {matched.cin}, not {cin}",
            )
        if gstin and matched.gstin and matched.gstin != gstin:
            return AnchorConflict(
                method=ResolutionMethod.IDENTIFIER_CONFLICT,
                reason=f"matched {matched.id} has GSTIN {matched.gstin}, not {gstin}",
            )
        # Before associating a new GSTIN, check whether its PAN already belongs to a
        # *different* company — that means the matched company and that other company
        # are the same legal entity (multi-state registration). We still match here,
        # but surface the pair for human merge instead of letting the duplicate sit.
        pan_merge_hint: uuid.UUID | None = None
        if gstin is not None and matched.gstin is None:
            pan = parse_gstin(gstin).pan
            others = [c for c in companies.find_by_pan(pan) if c.id != matched.id]
            if others:
                pan_merge_hint = others[0].id
        # Enrich the matched company with any identifier/domain it lacks, so a later
        # candidate carrying that identifier resolves instead of duplicating.
        if cin and matched.cin is None:
            matched.cin = cin
        companies.enrich(matched, gstin=gstin, domain=candidate.domain)
        return AnchorMatch(
            company=matched,
            created=False,
            matched_on=ResolutionMethod.CIN if cin_match else ResolutionMethod.GSTIN,
            pan_merge_hint=pan_merge_hint,
        )

    # No exact identifier match. Before creating, check whether the GSTIN's PAN
    # already belongs to a company — same legal entity, different state registration.
    # That is a human merge decision, not an automatic second company.
    if gstin is not None:
        pan = parse_gstin(gstin).pan
        pan_hits = companies.find_by_pan(pan)
        if pan_hits:
            return AnchorConflict(
                method=ResolutionMethod.PAN_MATCH,
                reason=f"GSTIN {gstin} shares PAN {pan} with {pan_hits[0].id} (different GSTIN)",
                hint_company_id=pan_hits[0].id,
            )

    # Genuinely new anchored company.
    created = companies.add(name=candidate.name, cin=cin, gstin=gstin, domain=candidate.domain)
    return AnchorMatch(company=created, created=True)
