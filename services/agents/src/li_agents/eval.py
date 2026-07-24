"""Precision-of-warm evaluation (PROJECT_SPEC.md §6, docs/ARCHITECTURE.md §12-T5).

The core P1 quality metric: of the accounts we called warm (or hot), what fraction
the customer agreed were worth pursuing. Computed per model_version so a scoring
change is measurable. This is the minimum eval depth at P1; richer replay tooling
comes later.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from li_core.models import ScoreBand

# A delivered account is "warm" (a positive prediction) if it scored warm or hot.
_POSITIVE_BANDS = frozenset({ScoreBand.WARM, ScoreBand.HOT})


@dataclass(frozen=True, slots=True)
class DeliveredOutcome:
    band: ScoreBand
    pursued: bool  # customer feedback: did they judge it worth pursuing?


@dataclass(frozen=True, slots=True)
class PrecisionReport:
    delivered_warm: int
    pursued: int

    @property
    def precision(self) -> float:
        """Fraction of warm-called accounts the customer pursued. Undefined (0.0)
        when nothing was called warm."""
        if self.delivered_warm == 0:
            return 0.0
        return self.pursued / self.delivered_warm


def precision_of_warm(outcomes: Iterable[DeliveredOutcome]) -> PrecisionReport:
    warm = [o for o in outcomes if o.band in _POSITIVE_BANDS]
    pursued = sum(1 for o in warm if o.pursued)
    return PrecisionReport(delivered_warm=len(warm), pursued=pursued)
