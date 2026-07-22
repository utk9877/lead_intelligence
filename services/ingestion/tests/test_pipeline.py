"""End-to-end within ingestion: fetch → snapshot → parse, with evidence integrity."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable

import pytest
from li_compliance.errors import DisallowedSourceError
from li_ingestion.adapters import NewsFundingAdapter
from li_ingestion.fetcher import CompliantFetcher
from li_ingestion.pipeline import ingest
from li_ingestion.snapshots import SnapshotWriter
from li_storage import InMemoryObjectStore

MakeFetcher = Callable[[dict[str, tuple[int, str, bytes]]], tuple[CompliantFetcher, object]]

FEED_ITEM = json.dumps(
    {
        "company_name": "Fictional Widgets Pvt Ltd",
        "company_domain": "fictional-widgets.test",
        "round": "Series A",
        "amount_inr_crore": 40,
        "published_at": "2026-05-10",
    }
).encode()

URL = "https://feeds.example-news.test/item/1"


def test_ingest_snapshots_before_parsing_and_hash_matches(make_fetcher: MakeFetcher) -> None:
    fetcher, _ = make_fetcher({URL: (200, "application/json", FEED_ITEM)})
    store = InMemoryObjectStore()
    outcome = ingest(NewsFundingAdapter(), fetcher, SnapshotWriter(store), URL)

    # Evidence exists and its hash is the SHA-256 of exactly the fetched bytes.
    assert outcome.evidence.content_hash == hashlib.sha256(FEED_ITEM).hexdigest()
    assert outcome.evidence.source_url == URL
    # The snapshot key resolves to the exact bytes (citation integrity).
    assert store.get(outcome.evidence.snapshot_key) == FEED_ITEM
    # And the parse produced the expected candidate.
    assert outcome.result.companies[0].name == "Fictional Widgets Pvt Ltd"


def test_ingesting_identical_content_twice_is_immutable(make_fetcher: MakeFetcher) -> None:
    fetcher, _ = make_fetcher({URL: (200, "application/json", FEED_ITEM)})
    store = InMemoryObjectStore()
    writer = SnapshotWriter(store)
    first = ingest(NewsFundingAdapter(), fetcher, writer, URL)
    second = ingest(NewsFundingAdapter(), fetcher, writer, URL)
    # Same bytes → same immutable snapshot key.
    assert first.evidence.snapshot_key == second.evidence.snapshot_key
    assert store.get(first.evidence.snapshot_key) == FEED_ITEM


def test_blocked_fetch_yields_no_snapshot(make_fetcher: MakeFetcher) -> None:
    # A disallowed URL never reaches the store — no orphan evidence.
    fetcher, _ = make_fetcher({})
    store = InMemoryObjectStore()
    bad = "https://linkedin.com/company/x"
    with pytest.raises(DisallowedSourceError):
        ingest(NewsFundingAdapter(), fetcher, SnapshotWriter(store), bad)
    assert store._objects == {}
