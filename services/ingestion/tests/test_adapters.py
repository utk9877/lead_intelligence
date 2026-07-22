"""Adapter parsing + the ADR-005 guarantee that posting-level adapters never leak
person data even when the source page contains it."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from li_compliance.guards import assert_company_level
from li_core.models import SignalType
from li_ingestion.adapters import (
    CareersPagesAdapter,
    JobBoardsAdapter,
    NewsFundingAdapter,
    RegistryGstAdapter,
    RegistryMcaAdapter,
    SiteTechAdapter,
)
from li_ingestion.artifacts import RawArtifact

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)

FICTIONAL_CIN = "U12345MH2019PTC123456"
FICTIONAL_GSTIN = "27ZZZZZ9999Z1Z8"


def artifact(
    source: str, url: str, body: bytes, content_type: str = "application/json"
) -> RawArtifact:
    return RawArtifact(source=source, url=url, fetched_at=NOW, content_type=content_type, body=body)


def test_registry_mca_parses_and_canonicalizes() -> None:
    body = json.dumps(
        {
            "cin": f"  {FICTIONAL_CIN.lower()} ",  # non-canonical input
            "name": "Fictional Widgets Pvt Ltd",
            "domain": "fictional-widgets.test",
            "incorporation_date": "2019-06-01",
        }
    ).encode()
    result = RegistryMcaAdapter().parse(artifact("registry_mca", "https://x.test", body))
    assert result.companies[0].cin == FICTIONAL_CIN  # canonicalized
    assert result.signals[0].type is SignalType.NEW_INCORPORATION


def test_registry_gst_emits_registration_only_when_active() -> None:
    active = json.dumps(
        {
            "gstin": FICTIONAL_GSTIN,
            "legal_name": "Fictional Widgets Pvt Ltd",
            "registration_date": "2019-06-05",
            "status": "Active",
        }
    ).encode()
    result = RegistryGstAdapter().parse(artifact("registry_gst", "https://x.test", active))
    assert result.companies[0].gstin == FICTIONAL_GSTIN
    assert [s.type for s in result.signals] == [SignalType.GST_REGISTRATION]

    cancelled = json.dumps(
        {
            "gstin": FICTIONAL_GSTIN,
            "legal_name": "X",
            "registration_date": "2019-06-05",
            "status": "Cancelled",
        }
    ).encode()
    result2 = RegistryGstAdapter().parse(artifact("registry_gst", "https://x.test", cancelled))
    assert result2.signals == []


def test_news_funding_parses_round() -> None:
    body = json.dumps(
        {
            "company_name": "Fictional Widgets Pvt Ltd",
            "company_domain": "fictional-widgets.test",
            "round": "Series A",
            "amount_inr_crore": 40,
            "investors": ["Fictional Ventures"],
            "published_at": "2026-05-10",
        }
    ).encode()
    result = NewsFundingAdapter().parse(artifact("news_funding", "https://x.test", body))
    assert result.signals[0].type is SignalType.FUNDING_ROUND
    assert result.signals[0].payload["amount_inr_crore"] == 40


def test_careers_page_is_posting_level_and_drops_person_data() -> None:
    # Source page deliberately carries recruiter person data; the adapter must
    # extract ONLY posting titles/counts and leak none of it (ADR-005).
    body = json.dumps(
        {
            "company_name": "Fictional Widgets Pvt Ltd",
            "company_domain": "fictional-widgets.test",
            "captured_at": "2026-07-20",
            "postings": [
                {"title": "SRE", "recruiter_email": "hr.person@fictional-widgets.test"},
                {"title": "Backend Engineer", "recruiter_name": "A. Person"},
                {"title": "SRE"},  # duplicate role
            ],
        }
    ).encode()
    result = CareersPagesAdapter().parse(artifact("careers_pages", "https://x.test", body))
    signal = result.signals[0]
    assert signal.type is SignalType.HIRING_SURGE
    assert signal.payload["open_postings"] == 3
    assert signal.payload["roles"] == ["Backend Engineer", "SRE"]  # deduped, no person data
    # The payload provably contains no person-shaped data.
    assert_company_level(dict(signal.payload), context="test")


def test_job_boards_posting_level() -> None:
    body = json.dumps(
        {
            "company_name": "Fictional Widgets Pvt Ltd",
            "captured_at": "2026-07-20",
            "postings": [{"title": "DevOps"}, {"title": "SRE"}],
        }
    ).encode()
    result = JobBoardsAdapter().parse(artifact("job_boards", "https://x.test", body))
    assert result.signals[0].payload["open_postings"] == 2


def test_site_tech_detects_stack() -> None:
    html = b"<html><script src='https://cdn.shopify.com/x.js'></script></html>"
    result = SiteTechAdapter("fictional-widgets.test").parse(
        artifact("site_tech", "https://www.example-co.test", html, content_type="text/html")
    )
    assert result.signals[0].type is SignalType.TECH_ADOPTION
    assert result.signals[0].payload["technologies"] == ["shopify"]


def test_site_tech_emits_nothing_when_no_stack_detected() -> None:
    result = SiteTechAdapter("plain.test").parse(
        artifact("site_tech", "https://www.example-co.test", b"<html></html>", "text/html")
    )
    assert result.signals == []


def test_site_tech_does_not_false_positive_on_vendor_name_in_prose() -> None:
    prose = b"<html><p>Our blog compares woocommerce vs shopify pricing.</p></html>"
    result = SiteTechAdapter("blog.test").parse(
        artifact("site_tech", "https://www.example-co.test", prose, "text/html")
    )
    assert result.signals == []  # anchored fingerprints, not bare words


def test_registry_mca_raises_on_missing_key() -> None:
    body = json.dumps({"name": "No CIN Co"}).encode()  # 'cin' absent
    with pytest.raises(KeyError):
        RegistryMcaAdapter().parse(artifact("registry_mca", "https://x.test", body))


def test_registry_mca_raises_on_malformed_date() -> None:
    body = json.dumps(
        {"cin": FICTIONAL_CIN, "name": "X", "incorporation_date": "not-a-date"}
    ).encode()
    with pytest.raises(ValueError, match="isoformat"):
        RegistryMcaAdapter().parse(artifact("registry_mca", "https://x.test", body))
