"""Value types passed between fetch → snapshot → normalize.

Deliberately company-level only (ADR-005): none of these carry person fields, and
`CandidateSignal.payload` is validated against the person-data guard before it is
ever constructed (see normalize.py).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from li_core.models import SignalType


@dataclass(frozen=True, slots=True)
class RawArtifact:
    """Exactly what a source returned, before interpretation. The bytes are what
    get snapshotted, so a citation always resolves to this precise content."""

    source: str  # adapter name
    url: str
    fetched_at: datetime
    content_type: str
    body: bytes


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """A stored, immutable snapshot — mirrors the li-db `evidence` row shape."""

    source_url: str
    content_hash: str
    snapshot_key: str
    captured_at: datetime


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
