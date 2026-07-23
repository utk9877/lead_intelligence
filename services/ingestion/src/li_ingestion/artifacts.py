"""Value types passed between fetch → snapshot → normalize.

Deliberately company-level only (ADR-005): none of these carry person fields, and
`CandidateSignal.payload` is validated against the person-data guard before it is
ever constructed (see normalize.py). CandidateCompany/CandidateSignal are the
shared domain types from li-core, re-exported here for the adapters' convenience.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from li_core.models import CandidateCompany, CandidateSignal

__all__ = ["CandidateCompany", "CandidateSignal", "EvidenceRecord", "RawArtifact"]


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
