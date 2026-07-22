"""Evidence snapshot writer: RawArtifact → immutable object-store snapshot.

The stored bytes are the artifact body verbatim; the returned EvidenceRecord's
content_hash is the SHA-256 of exactly those bytes, so `content_hash` and
`snapshot_key` always resolve to the same immutable object (docs/ARCHITECTURE.md §3).
"""

from __future__ import annotations

from li_storage import ObjectStore
from li_storage.store import sha256_hex

from li_ingestion.artifacts import EvidenceRecord, RawArtifact


class SnapshotWriter:
    def __init__(self, store: ObjectStore) -> None:
        self._store = store

    def write(self, artifact: RawArtifact) -> EvidenceRecord:
        key = self._store.put(artifact.body, content_type=artifact.content_type)
        return EvidenceRecord(
            source_url=artifact.url,
            content_hash=sha256_hex(artifact.body),
            snapshot_key=key,
            captured_at=artifact.fetched_at,
        )
