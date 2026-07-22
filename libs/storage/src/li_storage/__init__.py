"""Content-addressed object store for immutable evidence snapshots.

Ingestion writes snapshots here; agents (snapshot_read tool) and delivery read
them back. MinIO in local dev, S3 in AWS — identical client code (docs/ARCHITECTURE.md
§3). Not in the original §4 tree: added as a shared lib because writing (ingestion)
and reading (agents, delivery) span services, so the client cannot live in one.
"""

from li_storage.store import (
    InMemoryObjectStore,
    ObjectStore,
    S3ObjectStore,
    content_key,
)

__all__ = ["InMemoryObjectStore", "ObjectStore", "S3ObjectStore", "content_key"]
