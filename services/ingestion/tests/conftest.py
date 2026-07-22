"""Shared fixtures: a fictional allowed-sources registry and a fake transport.

All hosts are *.test (reserved, non-routable). No real company data appears.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

import pytest
from li_compliance.allowed_sources import AllowedSource, SourceKind, SourceRegistry
from li_compliance.robots import RobotsPolicy
from li_ingestion.fetcher import CompliantFetcher

FIXED_NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)

ALLOWED = (
    AllowedSource("registry_mca", SourceKind.REGISTRY_API, ("api.example-registry.test",)),
    AllowedSource("registry_gst", SourceKind.REGISTRY_API, ("api.example-registry.test",)),
    AllowedSource("news_funding", SourceKind.FEED, ("feeds.example-news.test",)),
    AllowedSource("careers_pages", SourceKind.CRAWL, ("careers.example-co.test",)),
    AllowedSource("job_boards", SourceKind.CRAWL, ("jobs.example-board.test",)),
    AllowedSource("site_tech", SourceKind.CRAWL, ("www.example-co.test",)),
)

ROBOTS_TXT = "User-agent: *\nDisallow: /private/\n"


@pytest.fixture
def registry() -> SourceRegistry:
    return SourceRegistry(ALLOWED)


@pytest.fixture
def robots() -> RobotsPolicy:
    return RobotsPolicy(lambda _origin: ROBOTS_TXT, user_agent="li-bot")


class FakeTransport:
    """Never follows redirects (matches the real transport contract). `redirects`
    maps a URL to a Location target, returned as a 302 so the fetcher follows it."""

    def __init__(
        self,
        responses: dict[str, tuple[int, str, bytes]],
        redirects: dict[str, str] | None = None,
    ) -> None:
        self.responses = responses
        self.redirects = redirects or {}
        self.calls: list[str] = []

    def __call__(self, url: str) -> tuple[int, str, bytes, str | None]:
        self.calls.append(url)
        location = self.redirects.get(url)
        if location is not None:
            return (302, "text/html", b"", location)
        if url not in self.responses:
            return (404, "text/plain", b"not found", None)
        status, content_type, body = self.responses[url]
        return (status, content_type, body, None)


MakeFetcher = Callable[..., tuple["CompliantFetcher", FakeTransport]]


@pytest.fixture
def make_fetcher(registry: SourceRegistry, robots: RobotsPolicy) -> MakeFetcher:
    def _make(
        responses: dict[str, tuple[int, str, bytes]],
        redirects: dict[str, str] | None = None,
    ) -> tuple[CompliantFetcher, FakeTransport]:
        transport = FakeTransport(responses, redirects)
        fetcher = CompliantFetcher(registry, transport, robots=robots, clock=lambda: FIXED_NOW)
        return fetcher, transport

    return _make
