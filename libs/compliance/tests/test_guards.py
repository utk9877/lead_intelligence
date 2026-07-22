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
    [
        "email",
        "first_name",
        "contactName",
        "LinkedIn_URL",
        "mobile",
        "din",  # exact short token
        "DIN",
        "date-of-birth",
        "designation",
        "director_name",
        "founder",
        "ceo",
        "email2",  # numbered variant
        "Contact-Email",
        "e_mail",
    ],
)
def test_person_shaped_keys_rejected_in_any_style(key: str) -> None:
    with pytest.raises(PersonDataError):
        assert_company_level({key: "x"}, context="test")


@pytest.mark.parametrize(
    "safe_key",
    ["coordinates", "heading", "din_verified_count", "revenue_inr", "founded_year"],
)
def test_company_level_keys_not_false_positives(safe_key: str) -> None:
    # "din" as an exact token must not trip on "coordinates"; "founded" not on "founder".
    assert_company_level({safe_key: 1}, context="test")


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


@pytest.mark.parametrize(
    "text",
    [
        "9876543210",  # bare 10 digits
        "+919876543210",
        "+91 9876543210",
        "+91 98765 43210",  # the common spaced form
        "+91-98765-43210",
        "98765 43210",
        "98765-43210",
        "919876543210",  # 91 prefix, no plus
        "call us at 98765.43210 today",
    ],
)
def test_indian_mobile_number_in_value_rejected(text: str) -> None:
    with pytest.raises(PersonDataError, match="Mobile number"):
        assert_company_level({"notes": text}, context="test")


def test_identifiers_are_not_false_positives() -> None:
    # CIN/GSTIN contain long digit runs; they must not trip the mobile pattern.
    assert_company_level(
        {"cin": "U12345MH2019PTC123456", "gstin": "27ZZZZZ9999Z1Z8", "revenue_inr": 91234567890},
        context="test",
    )


def test_context_is_attributed_in_error() -> None:
    with pytest.raises(PersonDataError, match=r"\[careers_pages\]"):
        assert_company_level({"email": "x"}, context="careers_pages")
