"""Non-DB: prove the synthetic GSTINs the golden set relies on are actually valid
and that same-PAN/different-state GSTINs really do share a PAN. Runs locally."""

from __future__ import annotations

from li_core.ids import gstin_check_char, is_valid_gstin, parse_gstin


def make_gstin(state: str, pan: str) -> str:
    first14 = f"{state}{pan}1Z"
    return first14 + gstin_check_char(first14)


def test_synthetic_gstins_pass_checksum() -> None:
    for state in ("27", "29", "07"):
        gstin = make_gstin(state, "AAACA1111A")
        assert is_valid_gstin(gstin), gstin


def test_same_pan_different_state_shares_pan() -> None:
    mh = parse_gstin(make_gstin("27", "AAACA1111A"))
    ka = parse_gstin(make_gstin("29", "AAACA1111A"))
    assert mh.pan == ka.pan == "AAACA1111A"
    assert mh.normalized != ka.normalized  # different GSTINs
    assert mh.state_code == "27"
    assert ka.state_code == "29"
