"""Person-data guards — ADR-005 enforced at the ingest boundary.

Company-level facts only. Any payload that carries person-shaped keys or values is
rejected before it can reach the graph. The stance is deliberately strict: a false
positive costs a human review; a false negative crosses the compliance boundary.
Company PAN is allowed (it is a company identifier and embedded in GSTIN); email
addresses of any kind are not — company-level intelligence needs none.

Known residual: bare personal *names* embedded in free-text values (e.g. a scraped
job title "Report to CEO A. Person") cannot be detected by pattern alone and are not
caught here. Adapters mitigate this structurally by extracting only company-level
fields (posting titles/counts, never free-form recruiter text); the human QA gate is
the backstop. Emails and Indian mobile numbers in values ARE caught.
"""

import re
import unicodedata
from collections.abc import Mapping, Sequence

from li_compliance.errors import PersonDataError

# Keys are normalized (NFKC, lowercased, everything but a-z stripped — so
# "Contact-Email", "email2", and fullwidth spellings all normalize) and then
# matched two ways: substring for unambiguous person tokens, exact for short
# tokens that would false-positive as substrings (e.g. "din" in "coordinates").
_FORBIDDEN_KEY_SUBSTRINGS = (
    "firstname",
    "lastname",
    "middlename",
    "fullname",
    "personname",
    "contactname",
    "contactperson",
    "email",
    "phone",
    "mobile",
    "whatsapp",
    "linkedin",
    "designation",
    "dateofbirth",
    "aadhaar",
    "aadhar",
    "director",
    "founder",
)
_FORBIDDEN_KEYS_EXACT = frozenset(
    {
        "dob",
        "din",  # director identification number — a person identifier
        "ceo",
        "cfo",
        "cto",
    }
)

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# Indian mobiles as commonly written: optional +91/91 prefix, then ten digits
# starting 6-9, tolerating space/dot/dash separators between digit groups.
_IN_MOBILE_RE = re.compile(r"(?<!\d)(?:\+?91[\s.\-]{0,2})?[6-9](?:[\s.\-]?\d){9}(?!\d)", re.ASCII)

_KEY_NORMALIZE_RE = re.compile(r"[^a-z]+")


def _normalize_key(key: str) -> str:
    return _KEY_NORMALIZE_RE.sub("", unicodedata.normalize("NFKC", key).lower())


def _key_is_forbidden(normalized: str) -> bool:
    if normalized in _FORBIDDEN_KEYS_EXACT:
        return True
    return any(token in normalized for token in _FORBIDDEN_KEY_SUBSTRINGS)


def _walk(value: object, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_str = str(key)
            if _key_is_forbidden(_normalize_key(key_str)):
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
