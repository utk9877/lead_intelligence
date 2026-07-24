"""Citation enforcement — the pipeline's hard rule (docs/ARCHITECTURE.md §2, §9).

A claim that does not join an evidence row cannot be rendered: `render_account_card`
raises. This is structural, not advisory — the "every claim links to its source"
promise of PROJECT_SPEC.md §3 is enforced here, once, for everything downstream.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable, Mapping
from typing import Any

from li_core.errors import LeadIntelligenceError
from li_core.models import Evidence

from li_agents.models import Claim, ResearchedAccount


class UncitedClaimError(LeadIntelligenceError):
    """A claim referenced an evidence id that isn't in the account's evidence set."""


class EvidenceSet:
    """The evidence available for one account, keyed by id."""

    def __init__(self, evidence: Iterable[Evidence]) -> None:
        self._by_id: dict[uuid.UUID, Evidence] = {e.id: e for e in evidence}

    def contains(self, evidence_id: uuid.UUID) -> bool:
        return evidence_id in self._by_id

    def get(self, evidence_id: uuid.UUID) -> Evidence:
        if evidence_id not in self._by_id:
            raise UncitedClaimError(f"no evidence with id {evidence_id}")
        return self._by_id[evidence_id]

    @property
    def ids(self) -> frozenset[uuid.UUID]:
        return frozenset(self._by_id)


def assert_cited(claim: Claim, evidence: EvidenceSet) -> None:
    if not evidence.contains(claim.evidence_id):
        raise UncitedClaimError(
            f"claim {claim.text!r} cites evidence {claim.evidence_id} not in the account's set"
        )


def render_account_card(account: ResearchedAccount, evidence: EvidenceSet) -> Mapping[str, Any]:
    """Render the delivered account card. Raises if ANY claim is uncited, so a card
    that reaches a customer always has every claim linked to a stored snapshot."""
    if not account.claims:
        raise UncitedClaimError("account has no cited claims; nothing to deliver")
    rendered_claims = []
    for claim in account.claims:
        source = evidence.get(claim.evidence_id)  # raises if missing
        rendered_claims.append(
            {
                "text": claim.text,
                "source_url": source.source_url,
                "snapshot_key": source.snapshot_key,
                "content_hash": source.content_hash,
            }
        )
    return {
        "company_id": str(account.company_id),
        "why_now": account.why_now,
        "why_fit": account.why_fit,
        "claims": rendered_claims,
    }
