"""CIN and GSTIN parsing and validation (ADR-001: the registry anchors).

CIN (Corporate Identification Number, 21 chars): structural validation only. MCA
publishes no check digit for CINs, and both the state-code and ownership-code sets
have been amended over time — a hardcoded membership list would reject valid
companies, so shape is validated here and the registry API stays the authority on
existence. Structure: listing letter (L/U) · 5-digit industry (NIC) code · 2-letter
state code · 4-digit incorporation year · 3-letter ownership code · 6-digit
registration number.

GSTIN (15 chars): 2-digit state code · 10-char PAN · entity code · literal 'Z' ·
check character, verified with the published mod-36 checksum.
"""

import re
from dataclasses import dataclass
from datetime import date

from li_core.errors import InvalidIdentifierError

_CIN_RE = re.compile(r"^([LU])(\d{5})([A-Z]{2})(\d{4})([A-Z]{3})(\d{6})$")
_GSTIN_RE = re.compile(r"^(\d{2})([A-Z]{5}\d{4}[A-Z])([1-9A-Z])Z([0-9A-Z])$")
_ALPHANUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_FIRST_COMPANIES_ACT_YEAR = 1850


@dataclass(frozen=True, slots=True)
class ParsedCin:
    listing: str  # "L" listed / "U" unlisted
    industry_code: str
    state_code: str
    year: int
    ownership_code: str
    registration_number: str


@dataclass(frozen=True, slots=True)
class ParsedGstin:
    state_code: str
    pan: str
    entity_code: str
    check_char: str


def parse_cin(raw: str) -> ParsedCin:
    value = raw.strip().upper()
    match = _CIN_RE.fullmatch(value)
    if match is None:
        raise InvalidIdentifierError(f"CIN has invalid structure: {raw!r}")
    year = int(match.group(4))
    if not _FIRST_COMPANIES_ACT_YEAR <= year <= date.today().year:
        raise InvalidIdentifierError(f"CIN incorporation year out of range: {raw!r}")
    return ParsedCin(
        listing=match.group(1),
        industry_code=match.group(2),
        state_code=match.group(3),
        year=year,
        ownership_code=match.group(5),
        registration_number=match.group(6),
    )


def gstin_check_char(first_14: str) -> str:
    """Mod-36 check character over the first 14 GSTIN characters."""
    if len(first_14) != 14:
        raise InvalidIdentifierError("GSTIN check input must be exactly 14 characters")
    total = 0
    for index, char in enumerate(first_14):
        if char not in _ALPHANUM:
            raise InvalidIdentifierError(f"GSTIN contains invalid character {char!r}")
        product = _ALPHANUM.index(char) * (2 if index % 2 else 1)
        total += product // 36 + product % 36
    return _ALPHANUM[(36 - total % 36) % 36]


def parse_gstin(raw: str) -> ParsedGstin:
    value = raw.strip().upper()
    match = _GSTIN_RE.fullmatch(value)
    if match is None:
        raise InvalidIdentifierError(f"GSTIN has invalid structure: {raw!r}")
    if match.group(1) == "00":
        raise InvalidIdentifierError(f"GSTIN state code cannot be 00: {raw!r}")
    expected = gstin_check_char(value[:14])
    if match.group(4) != expected:
        raise InvalidIdentifierError(f"GSTIN check character mismatch: {raw!r}")
    return ParsedGstin(
        state_code=match.group(1),
        pan=match.group(2),
        entity_code=match.group(3),
        check_char=match.group(4),
    )


def is_valid_cin(raw: str) -> bool:
    try:
        parse_cin(raw)
    except InvalidIdentifierError:
        return False
    return True


def is_valid_gstin(raw: str) -> bool:
    try:
        parse_gstin(raw)
    except InvalidIdentifierError:
        return False
    return True
