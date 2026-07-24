from decimal import Decimal

import pytest
from li_llm.budget import BudgetExceededError, BudgetGuard


def test_charges_accumulate() -> None:
    guard = BudgetGuard(Decimal("100"))
    guard.charge(Decimal("30"))
    guard.charge(Decimal("20"))
    assert guard.spent == Decimal("50")
    assert guard.remaining == Decimal("50")


def test_exact_cap_does_not_raise() -> None:
    guard = BudgetGuard(Decimal("100"))
    guard.charge(Decimal("100"))  # spent == cap is allowed
    assert guard.remaining == Decimal("0")


def test_exceeding_cap_raises_and_counts_the_breaching_charge() -> None:
    guard = BudgetGuard(Decimal("100"))
    guard.charge(Decimal("80"))
    with pytest.raises(BudgetExceededError):
        guard.charge(Decimal("30"))
    # The breaching charge is still counted, so the ledger reflects what tripped it.
    assert guard.spent == Decimal("110")
