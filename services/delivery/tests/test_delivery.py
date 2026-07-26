"""Unit tests for the pure delivery modules: cards, Slack, CRM stubs, reporting."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from li_agents.evidence import EvidenceSet, UncitedClaimError
from li_agents.models import AccountScore, Claim, ResearchedAccount
from li_core.models import Evidence, ScoreBand
from li_delivery.cards import NotDeliverableError, render_delivery_card
from li_delivery.crm import CrmNotConfiguredError, CrmSync, HubSpotSync, ZohoSync
from li_delivery.reporting import format_cost_report
from li_delivery.slack import SlackDeliveryError, card_to_blocks, deliver_to_slack

NOW = datetime(2026, 7, 26, tzinfo=UTC)
EV = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
COMPANY = uuid.uuid4()


def _evidence_set() -> EvidenceSet:
    return EvidenceSet(
        [
            Evidence(
                id=EV,
                source_url="https://x.test/1",
                content_hash="0" * 64,
                snapshot_key="k",
                captured_at=NOW,
            )
        ]
    )


def _account() -> ResearchedAccount:
    return ResearchedAccount(
        company_id=COMPANY,
        why_now="Raised Series A",
        why_fit="Fits DevOps SaaS",
        claims=(Claim("Series A", EV),),
    )


def _score(band: ScoreBand) -> AccountScore:
    return AccountScore(
        value=82.0, band=band, rubric_version="r1", model_version="claude-sonnet-5", rationale="x"
    )


def test_warm_account_renders_a_card() -> None:
    card = render_delivery_card(_account(), _score(ScoreBand.WARM), _evidence_set())
    assert card["band"] == "warm"
    assert card["claims"][0]["source_url"] == "https://x.test/1"


def test_not_warm_account_is_not_delivered() -> None:
    with pytest.raises(NotDeliverableError):
        render_delivery_card(_account(), _score(ScoreBand.NOT_WARM), _evidence_set())


def test_uncited_claim_still_blocks_delivery() -> None:
    account = ResearchedAccount(
        company_id=COMPANY, why_now="n", why_fit="f", claims=(Claim("fabricated", uuid.uuid4()),)
    )
    with pytest.raises(UncitedClaimError):
        render_delivery_card(account, _score(ScoreBand.HOT), _evidence_set())


def test_card_to_blocks_has_a_citation_per_claim() -> None:
    card = render_delivery_card(_account(), _score(ScoreBand.HOT), _evidence_set())
    blocks = card_to_blocks(card)
    # header + why_now + why_fit + divider + one claim section
    assert blocks[0]["type"] == "header"
    assert any("source" in b.get("text", {}).get("text", "") for b in blocks)


def test_slack_escapes_mrkdwn_control_chars() -> None:
    # A claim text with mrkdwn/broadcast chars must be neutralised (no live @here).
    account = ResearchedAccount(
        company_id=COMPANY, why_now="<!here> ping", why_fit="a & b", claims=(Claim("<script>", EV),)
    )
    blocks = card_to_blocks(render_delivery_card(account, _score(ScoreBand.WARM), _evidence_set()))
    rendered = "".join(b.get("text", {}).get("text", "") for b in blocks if b["type"] == "section")
    assert "<!here>" not in rendered  # escaped to &lt;!here&gt;
    assert "&lt;!here&gt;" in rendered
    assert "<script>" not in rendered and "&lt;script&gt;" in rendered


def test_slack_degrades_a_malicious_source_url_to_plain_text() -> None:
    ev_id = uuid.uuid4()
    evidence = EvidenceSet(
        [
            Evidence(
                id=ev_id,
                source_url="https://x.test/1|@channel>ping",
                content_hash="0" * 64,
                snapshot_key="k",
                captured_at=NOW,
            )
        ]
    )
    account = ResearchedAccount(
        company_id=COMPANY, why_now="n", why_fit="f", claims=(Claim("c", ev_id),)
    )
    blocks = card_to_blocks(render_delivery_card(account, _score(ScoreBand.WARM), evidence))
    rendered = "".join(b.get("text", {}).get("text", "") for b in blocks if b["type"] == "section")
    # The dangerous URL never becomes a live <...|...> link.
    assert "<https://x.test/1|@channel>" not in rendered


def test_slack_delivery_ok_and_error() -> None:
    card = render_delivery_card(_account(), _score(ScoreBand.WARM), _evidence_set())
    sent: list[tuple[str, dict[str, Any]]] = []

    def ok_transport(url: str, body: dict[str, Any]) -> int:
        sent.append((url, body))
        return 200

    deliver_to_slack(ok_transport, "https://hooks.slack.test/x", card)
    assert sent[0][0] == "https://hooks.slack.test/x"

    with pytest.raises(SlackDeliveryError):
        deliver_to_slack(lambda _u, _b: 500, "https://hooks.slack.test/x", card)


def test_crm_stubs_conform_to_protocol_and_refuse() -> None:
    for sync in (HubSpotSync(), ZohoSync()):
        assert isinstance(sync, CrmSync)
        with pytest.raises(CrmNotConfiguredError):
            sync.push_account({})


def test_cost_report_computes_per_account() -> None:
    report = format_cost_report(
        {"pass1_triggers": Decimal("83.00"), "pass2_research": Decimal("166.00")},
        delivered_accounts=1,
    )
    assert "illustrative" in report
    assert "249.00" in report  # total, and ₹/account (1 delivered)
    assert "₹/account" in report


def test_cost_report_handles_zero_accounts() -> None:
    report = format_cost_report({"pass1_triggers": Decimal("83.00")}, delivered_accounts=0)
    assert "0.00" in report  # per-account is 0, no division by zero
    assert "83.00" in report
