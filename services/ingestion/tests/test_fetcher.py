"""The compliance gate is the reason this service is safe. These tests are
load-bearing: never weaken them to make an adapter fetch something new."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from li_compliance.errors import DisallowedSourceError
from li_ingestion.fetcher import CompliantFetcher, FetchBlockedError

MakeFetcher = Callable[[dict[str, tuple[int, str, bytes]]], tuple[CompliantFetcher, object]]

OK = (200, "application/json", b"{}")


def test_unlisted_source_is_blocked(make_fetcher: MakeFetcher) -> None:
    fetcher, transport = make_fetcher({"https://linkedin.com/company/x": OK})
    with pytest.raises(DisallowedSourceError):
        fetcher.fetch("https://linkedin.com/company/x", source_name="news_funding")
    # The block happens BEFORE any transport call.
    assert transport.calls == []  # type: ignore[attr-defined]


def test_allowed_registry_source_fetches(make_fetcher: MakeFetcher) -> None:
    url = "https://api.example-registry.test/company/U12345MH2019PTC123456"
    fetcher, _ = make_fetcher({url: OK})
    artifact = fetcher.fetch(url, source_name="registry_mca")
    assert artifact.url == url
    assert artifact.source == "registry_mca"


def test_robots_disallowed_crawl_is_blocked(make_fetcher: MakeFetcher) -> None:
    url = "https://careers.example-co.test/private/secret"
    fetcher, transport = make_fetcher({url: OK})
    with pytest.raises(FetchBlockedError):
        fetcher.fetch(url, source_name="careers_pages")
    assert transport.calls == []  # type: ignore[attr-defined]


def test_robots_allowed_crawl_fetches(make_fetcher: MakeFetcher) -> None:
    url = "https://careers.example-co.test/jobs"
    fetcher, _ = make_fetcher({url: (200, "text/html", b"<html></html>")})
    artifact = fetcher.fetch(url, source_name="careers_pages")
    assert artifact.body == b"<html></html>"


def test_http_error_status_raises(make_fetcher: MakeFetcher) -> None:
    url = "https://api.example-registry.test/company/missing"
    fetcher, _ = make_fetcher({url: (500, "text/plain", b"boom")})
    with pytest.raises(FetchBlockedError, match="HTTP 500"):
        fetcher.fetch(url, source_name="registry_mca")


def test_missing_url_treated_as_404(make_fetcher: MakeFetcher) -> None:
    url = "https://api.example-registry.test/company/absent"
    fetcher, _ = make_fetcher({})  # transport returns 404 for anything
    with pytest.raises(FetchBlockedError, match="HTTP 404"):
        fetcher.fetch(url, source_name="registry_mca")
