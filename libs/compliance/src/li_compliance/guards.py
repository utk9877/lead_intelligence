"""Person-data guards — ADR-005 enforced at the ingest boundary.

Company-level facts only. Any payload that carries person-shaped keys or values is
rejected before it can reach the graph. The stance is deliberately strict: a false
positive costs a human review; a false negative crosses the compliance boundary.
Company PAN is allowed (it is a company identifier and embedded in GSTIN); email
addresses of any kind are not — company-level intelligence needs none.
"""

import re
from collections.abc import Mapping, Sequence

from li_compliance.errors import PersonDataError

# Keys are normalized (lowercased, non-alphanumeric stripped) before matching.
_FORBIDDEN_KEYS = frozenset(
    {
        "firstname",
        "lastname",
        "middlename",
        "fullname",
        "personname",
        "contactname",
        "contactperson",
        "email",
        "emailaddress",
        "contactemail",
        "personalemail",
        "phone",
        "phonenumber",
        "contactphone",
        "mobile",
        "mobilenumber",
        "whatsapp",
        "linkedin",
        "linkedinurl",
        "designationholder",
        "dob",
        "dateofbirth",
        "aadhaar",
        "aadhar",
        "din",  # director identification number — a person identifier
    }
)

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_IN_MOBILE_RE = re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)")

_KEY_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def _normalize_key(key: str) -> str:
    return _KEY_NORMALIZE_RE.sub("", key.lower())


def _walk(value: object, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_str = str(key)
            if _normalize_key(key_str) in _FORBIDDEN_KEYS:
                raise PersonDataError(
                    f"Person-shaped key {key_str!r} at {path or 'payload root'} (ADR-005)"
                )
            _walk(child, f"{path}.{key_str}" if path else key_str)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _walk(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if _EMAIL_RE.search(value):
            raise PersonDataError(f"Email address found in value at {path!r} (ADR-005)")
        if _IN_MOBILE_RE.search(value):
            raise PersonDataError(f"Mobile number found in value at {path!r} (ADR-005)")


def assert_company_level(payload: Mapping[str, object], *, context: str) -> None:
    """Raise PersonDataError if the payload carries person-shaped data.

    `context` names the boundary being crossed (e.g. an adapter name) so
    violations are attributable in logs.
    """
    try:
        _walk(payload, "")
    except PersonDataError as error:
        raise PersonDataError(f"[{context}] {error}") from None
