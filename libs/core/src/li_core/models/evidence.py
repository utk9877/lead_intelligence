from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Evidence:
    """An immutable snapshot of a cited source page.

    `snapshot_key` addresses the stored copy (MinIO/S3, content-hash keyed) so
    citations survive the source page changing or dying.
    """

    id: UUID
    source_url: str
    content_hash: str
    snapshot_key: str
    captured_at: datetime
