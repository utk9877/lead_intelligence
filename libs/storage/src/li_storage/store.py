"""Object store: content-addressed, write-once.

The key is derived from the SHA-256 of the content, so identical bytes always map
to the same key and a re-store is a verified no-op — snapshots are immutable by
construction (docs/ARCHITECTURE.md §3: citations survive source pages changing).
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_key(data: bytes, *, prefix: str = "snapshots") -> str:
    """Fan-out key `<prefix>/<hh>/<full-sha256>` — the hash IS the address."""
    digest = sha256_hex(data)
    return f"{prefix}/{digest[:2]}/{digest}"


@runtime_checkable
class ObjectStore(Protocol):
    def put(self, data: bytes, *, content_type: str = "application/octet-stream") -> str:
        """Store bytes; return their content key. Idempotent for identical bytes."""
        ...

    def get(self, key: str) -> bytes: ...

    def exists(self, key: str) -> bool: ...


class InMemoryObjectStore:
    """Dev/test backend. Same content-addressed semantics as S3."""

    def __init__(self, prefix: str = "snapshots") -> None:
        self._prefix = prefix
        self._objects: dict[str, bytes] = {}

    def put(self, data: bytes, *, content_type: str = "application/octet-stream") -> str:
        key = content_key(data, prefix=self._prefix)
        # Write-once: identical content re-hashes to the same key; never overwrite.
        self._objects.setdefault(key, data)
        return key

    def get(self, key: str) -> bytes:
        return self._objects[key]

    def exists(self, key: str) -> bool:
        return key in self._objects


class S3ObjectStore:
    """S3/MinIO backend. Bucket + client are injected (li-llm-style seam)."""

    def __init__(self, client: S3Client, bucket: str, prefix: str = "snapshots") -> None:
        self._client = client
        self._bucket = bucket
        self._prefix = prefix

    def put(self, data: bytes, *, content_type: str = "application/octet-stream") -> str:
        key = content_key(data, prefix=self._prefix)
        if not self.exists(key):
            self._client.put_object(
                Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
            )
        return key

    def get(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        body: bytes = response["Body"].read()
        return body

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as error:
            if error.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
                return False
            raise
        return True
