from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Company:
    """A company-level entity, anchored on CIN/GSTIN where available (ADR-001).

    Company-level facts only — person-level fields must never be added (ADR-005).
    """

    id: UUID
    name: str
    cin: str | None = None
    gstin: str | None = None
    domain: str | None = None
