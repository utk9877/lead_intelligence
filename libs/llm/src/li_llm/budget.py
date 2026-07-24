"""Per-account budget caps — the kill-switch for runaway agent loops.

A single researched account has a hard ₹ ceiling; when the running spend crosses
it, the next charge raises and the pass aborts (docs/ARCHITECTURE.md §2, §10).
"""

from __future__ import annotations

from decimal import Decimal

from li_core.errors import LeadIntelligenceError


class BudgetExceededError(LeadIntelligenceError):
    """The per-account spend cap was crossed; the caller must stop."""


class BudgetGuard:
    def __init__(self, cap_inr: Decimal) -> None:
        self._cap = cap_inr
        self._spent = Decimal("0")

    @property
    def spent(self) -> Decimal:
        return self._spent

    @property
    def remaining(self) -> Decimal:
        return self._cap - self._spent

    def charge(self, amount_inr: Decimal) -> None:
        """Add to running spend; raise if the cap is now exceeded. The breaching
        charge is still counted, so the ledger records what tripped the cap."""
        self._spent += amount_inr
        if self._spent > self._cap:
            raise BudgetExceededError(
                f"per-account budget ₹{self._cap} exceeded (spent ₹{self._spent})"
            )
