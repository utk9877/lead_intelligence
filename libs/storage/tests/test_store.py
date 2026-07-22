import boto3
import pytest
from li_storage import InMemoryObjectStore, ObjectStore, S3ObjectStore, content_key
from li_storage.store import sha256_hex
from moto import mock_aws

BODY = b"<html>fictional evidence page</html>"


def _store_contract(store: ObjectStore) -> None:
    key = store.put(BODY, content_type="text/html")
    assert store.exists(key)
    assert store.get(key) == BODY
    # Content-addressed: same bytes -> same key (idempotent, immutable).
    assert store.put(BODY) == key
    # Different bytes -> different key.
    other = store.put(b"different", content_type="text/plain")
    assert other != key


def test_content_key_is_sha256_addressed() -> None:
    key = content_key(BODY)
    assert key == f"snapshots/{sha256_hex(BODY)[:2]}/{sha256_hex(BODY)}"


def test_inmemory_store_contract() -> None:
    _store_contract(InMemoryObjectStore())


def test_inmemory_missing_key_raises() -> None:
    with pytest.raises(KeyError):
        InMemoryObjectStore().get("snapshots/aa/does-not-exist")


def test_inmemory_write_once_does_not_overwrite() -> None:
    store = InMemoryObjectStore()
    key = store.put(BODY)
    # Re-put identical content is a verified no-op; the stored bytes are unchanged.
    assert store.put(BODY) == key
    assert store.get(key) == BODY


@mock_aws
def test_s3_store_contract() -> None:
    client = boto3.client("s3", region_name="ap-south-1")
    client.create_bucket(
        Bucket="evidence-test",
        CreateBucketConfiguration={"LocationConstraint": "ap-south-1"},
    )
    store = S3ObjectStore(client, bucket="evidence-test")
    _store_contract(store)


@mock_aws
def test_s3_and_inmemory_produce_identical_keys() -> None:
    client = boto3.client("s3", region_name="ap-south-1")
    client.create_bucket(
        Bucket="evidence-test",
        CreateBucketConfiguration={"LocationConstraint": "ap-south-1"},
    )
    s3 = S3ObjectStore(client, bucket="evidence-test")
    mem = InMemoryObjectStore()
    assert s3.put(BODY) == mem.put(BODY)  # same code path, portable citations


@mock_aws
def test_s3_exists_false_for_absent_key() -> None:
    client = boto3.client("s3", region_name="ap-south-1")
    client.create_bucket(
        Bucket="evidence-test",
        CreateBucketConfiguration={"LocationConstraint": "ap-south-1"},
    )
    store = S3ObjectStore(client, bucket="evidence-test")
    assert not store.exists("snapshots/aa/absent")
