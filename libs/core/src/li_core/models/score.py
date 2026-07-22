from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class ScoreBand(StrEnum):
    """Warm/hot are bands on one numeric score, tuned by customer feedback."""

    HOT = "hot"
    WARM = "warm"
    NOT_WARM = "not_warm"


@dataclass(frozen=True, slots=True)
class Score:
    company_id: UUID
    customer_id: UUID
    value: float
    band: ScoreBand
    rubric_version: str
    model_version: str
    created_at: datetime
