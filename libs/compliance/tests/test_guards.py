import pytest
from li_compliance.errors import PersonDataError
from li_compliance.guards import assert_company_level

COMPANY_LEVEL_PAYLOAD: dict[str, object] = {
    "name": "Fictional Widgets Pvt Ltd",
    "cin": "U12345MH2019PTC123456",
    "gstin": "27ZZZZZ9999Z1Z8",
    "domain": "fictional-widgets.test",
    "signals": [
        {"type": "hiring_surge", "open_postings": 14, "roles": ["DevOps", "SRE"]},
        {"type": "funding_round", "round": "Series A", "amount_inr_crore": 40},
    ],
    "pan": "ZZZZZ9999Z",  # company PAN is a company identifier — allowed
}


def test_company_level_payload_passes() -> None:
    assert_company_level(COMPANY_LEVEL_PAYLOAD, context="test")


@pytest.mark.parametrize(
    "key",
    ["email", "first_name", "contactName", "LinkedIn_URL", "mobile", "din", "date-of-birth"],
)
def test_person_shaped_keys_rejected_in_any_style(key: str) -> None:
    with pytest.raises(PersonDataError):
        assert_company_level({key: "x"}, context="test")


def test_nested_person_key_rejected() -> None:
    payload: dict[str, object] = {
        "name": "Fictional Widgets Pvt Ltd",
        "postings": [{"title": "SRE", "recruiter": {"email": "someone@example.test"}}],
    }
    with pytest.raises(PersonDataError, match="email"):
        assert_company_level(payload, context="test")


def test_email_address_in_value_rejected() -> None:
    with pytest.raises(PersonDataError, match="Email address"):
        assert_company_level(
            {"description": "Apply to hr.person@fictional-widgets.test today"},
            context="test",
        )


def test_indian_mobile_number_in_value_rejected() -> None:
    with pytest.raises(PersonDataError, match="Mobile number"):
        assert_company_level({"notes": "call +91 98765 43210".replace(" ", "")}, context="test")


def test_identifiers_are_not_false_positives() -> None:
    # CIN/GSTIN contain long digit runs; they must not trip the mobile pattern.
    assert_company_level(
        {"cin": "U12345MH2019PTC123456", "gstin": "27ZZZZZ9999Z1Z8", "revenue_inr": 91234567890},
        context="test",
    )


def test_context_is_attributed_in_error() -> None:
    with pytest.raises(PersonDataError, match=r"\[careers_pages\]"):
        assert_company_level({"email": "x"}, context="careers_pages")
