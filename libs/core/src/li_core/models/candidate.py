"""Pre-resolution candidate value objects.

Emitted by ingestion adapters, consumed by the resolver. Shared here (not in a
service) because both sides need them. Company-level only (ADR-005).
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from li_core.models.signal import SignalType


@dataclass(frozen=True, slots=True)
class CandidateCompany:
    name: str
    cin: str | None = None
    gstin: str | None = None
    domain: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateSignal:
    type: SignalType
    observed_at: datetime
    payload: Mapping[str, object] = field(default_factory=dict)
