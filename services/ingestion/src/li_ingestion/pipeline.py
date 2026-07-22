"""Ties fetch → snapshot → parse into one ingest step.

Evidence-first ordering is deliberate: the artifact is snapshotted BEFORE it is
parsed, so anything the parser later cites already has an immutable snapshot to
resolve to. There is no path that yields candidates without stored evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from li_ingestion.adapters.base import Adapter, AdapterResult
from li_ingestion.artifacts import EvidenceRecord
from li_ingestion.fetcher import CompliantFetcher
from li_ingestion.snapshots import SnapshotWriter


@dataclass(frozen=True, slots=True)
class IngestOutcome:
    evidence: EvidenceRecord
    result: AdapterResult


def ingest(
    adapter: Adapter,
    fetcher: CompliantFetcher,
    snapshots: SnapshotWriter,
    url: str,
) -> IngestOutcome:
    artifact = adapter.fetch(fetcher, url)  # compliance gate runs here
    evidence = snapshots.write(artifact)  # immutable snapshot BEFORE parse
    result = adapter.parse(artifact)
    return IngestOutcome(evidence=evidence, result=result)
