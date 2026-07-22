from datetime import UTC, datetime

import pytest
from li_compliance.errors import PersonDataError
from li_core.models import SignalType
from li_ingestion.normalize import build_signal, posting_summary

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)


def test_build_signal_rejects_person_payload() -> None:
    # The ingest boundary refuses person data rather than writing then cleaning up.
    with pytest.raises(PersonDataError):
        build_signal(
            signal_type=SignalType.HIRING_SURGE,
            observed_at=NOW,
            payload={"open_postings": 3, "recruiter_email": "p@x.test"},
            context="careers_pages",
        )


def test_build_signal_accepts_company_level_payload() -> None:
    signal = build_signal(
        signal_type=SignalType.FUNDING_ROUND,
        observed_at=NOW,
        payload={"round": "Series A", "amount_inr_crore": 40},
        context="news_funding",
    )
    assert signal.type is SignalType.FUNDING_ROUND


def test_posting_summary_dedups_and_sorts_roles() -> None:
    assert posting_summary(["SRE", "DevOps", "SRE"], open_count=3) == {
        "open_postings": 3,
        "roles": ["DevOps", "SRE"],
    }
