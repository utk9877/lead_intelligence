import uuid

import pytest
from agents_fixtures import EV_FUNDING, EV_HIRING
from li_agents.evidence import EvidenceSet, UncitedClaimError, render_account_card
from li_agents.models import Claim, ResearchedAccount

COMPANY = uuid.uuid4()


def _account(*claims: Claim) -> ResearchedAccount:
    return ResearchedAccount(company_id=COMPANY, why_now="now", why_fit="fit", claims=claims)


def test_cited_account_renders_with_sources(evidence_set: EvidenceSet) -> None:
    card = render_account_card(
        _account(Claim("Raised Series A", EV_FUNDING), Claim("Hiring DevOps", EV_HIRING)),
        evidence_set,
    )
    assert len(card["claims"]) == 2
    assert card["claims"][0]["source_url"].startswith("https://")
    assert card["claims"][0]["snapshot_key"]  # citation resolves to a snapshot


def test_uncited_claim_fails_rendering(evidence_set: EvidenceSet) -> None:
    stranger = uuid.uuid4()
    with pytest.raises(UncitedClaimError):
        render_account_card(_account(Claim("Unbacked claim", stranger)), evidence_set)


def test_account_with_no_claims_cannot_be_delivered(evidence_set: EvidenceSet) -> None:
    with pytest.raises(UncitedClaimError, match="no cited claims"):
        render_account_card(_account(), evidence_set)
