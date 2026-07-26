"""Account-card rendering for delivery.

The QA-approved, evidence-cited account becomes a card the customer reads. It reuses
li-agents' render_account_card, which FAILS if any claim is uncited — so a delivered
card always has every claim linked to a stored snapshot (docs/ARCHITECTURE.md §9).
Warm/hot are bands on the score; both are delivered, "not_warm" is not.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from li_agents.evidence import EvidenceSet, render_account_card
from li_agents.models import AccountScore, ResearchedAccount
from li_core.errors import LeadIntelligenceError
from li_core.models import ScoreBand

_DELIVERABLE_BANDS = frozenset({ScoreBand.WARM, ScoreBand.HOT})


class NotDeliverableError(LeadIntelligenceError):
    """The account is below the warm threshold and must not be delivered."""


def render_delivery_card(
    account: ResearchedAccount, score: AccountScore, evidence: EvidenceSet
) -> Mapping[str, Any]:
    if score.band not in _DELIVERABLE_BANDS:
        raise NotDeliverableError(f"band {score.band.value} is below the warm threshold")
    card = dict(render_account_card(account, evidence))  # raises on any uncited claim
    card["band"] = score.band.value
    card["score"] = score.value
    return card
