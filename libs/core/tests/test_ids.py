import pytest
from li_core.errors import InvalidIdentifierError
from li_core.ids import (
    gstin_check_char,
    is_valid_cin,
    is_valid_gstin,
    parse_cin,
    parse_gstin,
)

# Fictional but structurally valid CIN (obviously fake registration number).
FICTIONAL_CIN = "U12345MH2019PTC123456"

# Widely published sample GSTIN from GST documentation; our mod-36 implementation
# was cross-checked against its known check character 'V'.
SAMPLE_GSTIN = "27AAPFU0939F1ZV"

# Fictional GSTIN: base 27ZZZZZ9999Z1Z, check char computed by the published
# mod-36 algorithm (verified against SAMPLE_GSTIN above, so not self-referential).
FICTIONAL_GSTIN = "27ZZZZZ9999Z1Z8"


class TestCin:
    def test_valid_cin_parses(self) -> None:
        parsed = parse_cin(FICTIONAL_CIN)
        assert parsed.listing == "U"
        assert parsed.industry_code == "12345"
        assert parsed.state_code == "MH"
        assert parsed.year == 2019
        assert parsed.ownership_code == "PTC"
        assert parsed.registration_number == "123456"

    def test_lowercase_and_whitespace_normalized(self) -> None:
        assert is_valid_cin("  u12345mh2019ptc123456 ")
        # The canonical form is exposed for storage — never the raw input.
        assert parse_cin("  u12345mh2019ptc123456 ").normalized == FICTIONAL_CIN

    @pytest.mark.parametrize(
        "boundary_year,valid",
        [(1850, True), (2019, True), (2026, True), (1849, False)],
    )
    def test_cin_year_boundaries(self, boundary_year: int, valid: bool) -> None:
        cin = f"U12345MH{boundary_year}PTC123456"
        assert is_valid_cin(cin) is valid

    @pytest.mark.parametrize(
        "bad",
        [
            "",
            "X12345MH2019PTC123456",  # listing must be L or U
            "U12345MH2019PTC12345",  # too short
            "U12345MH2019PTC1234567",  # too long
            "U12345MH1849PTC123456",  # year before companies legislation
            "U12345MH2999PTC123456",  # year in the future
            "U12345M92019PTC123456",  # digit in state code
            "U1234!MH2019PTC123456",  # invalid character
        ],
    )
    def test_invalid_cin_rejected(self, bad: str) -> None:
        assert not is_valid_cin(bad)
        with pytest.raises(InvalidIdentifierError):
            parse_cin(bad)

    def test_non_ascii_digits_rejected(self) -> None:
        # Built via chr() so no ambiguous glyphs appear in source. re.ASCII must
        # keep fullwidth (U+FF10..) and Devanagari (U+0966..) digits out of \d,
        # or they would pollute the canonical identifier and defeat dedup.
        fullwidth = "".join(chr(0xFF10 + int(d)) for d in "12345")
        devanagari = "".join(chr(0x0966 + int(d)) for d in "12345")
        assert not is_valid_cin(f"U{fullwidth}MH2019PTC123456")
        assert not is_valid_cin(f"U{devanagari}DL2020PTC123456")


class TestGstin:
    def test_published_sample_is_valid(self) -> None:
        parsed = parse_gstin(SAMPLE_GSTIN)
        assert parsed.state_code == "27"
        assert parsed.pan == "AAPFU0939F"
        assert parsed.entity_code == "1"
        assert parsed.check_char == "V"

    def test_fictional_vector_is_valid(self) -> None:
        assert is_valid_gstin(FICTIONAL_GSTIN)

    def test_check_char_computation(self) -> None:
        assert gstin_check_char(SAMPLE_GSTIN[:14]) == "V"
        assert gstin_check_char(FICTIONAL_GSTIN[:14]) == "8"

    def test_every_single_character_mutation_breaks_validity(self) -> None:
        for position in range(len(SAMPLE_GSTIN)):
            original = SAMPLE_GSTIN[position]
            for replacement in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                if replacement == original:
                    continue
                mutated = SAMPLE_GSTIN[:position] + replacement + SAMPLE_GSTIN[position + 1 :]
                assert not is_valid_gstin(mutated), f"mutation accepted: {mutated}"

    @pytest.mark.parametrize(
        "bad",
        [
            "",
            "00ZZZZZ9999Z1Z8",  # state code 00
            "27ZZZZZ9999Z1Y8",  # 14th char must be literal Z
            "27ZZZZZ9999Z1Z",  # too short
            "27zzzzz9999z1z88",  # too long
        ],
    )
    def test_invalid_gstin_rejected(self, bad: str) -> None:
        assert not is_valid_gstin(bad)

    def test_check_char_requires_14_chars(self) -> None:
        with pytest.raises(InvalidIdentifierError):
            gstin_check_char("27ZZZZZ9999Z1")
