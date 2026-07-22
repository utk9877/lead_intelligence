"""The compliance gate every fetch passes through (docs/ARCHITECTURE.md §1, RISKS.md#data-tos).

Two checks, in order, before any byte leaves the network:
  1. `allowed_sources.require_allowed(url)` — unlisted host → DisallowedSourceError.
  2. For crawl sources honoring robots, `robots.can_fetch(url)` — blocked → FetchBlockedError.

The HTTP transport is injected so tests never touch the network. There is no code
path that fetches without passing the registry check first — that is the point.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from li_compliance.allowed_sources import SourceKind, SourceRegistry
from li_compliance.errors import ComplianceError
from li_compliance.robots import RobotsPolicy

from li_ingestion.artifacts import RawArtifact


class FetchBlockedError(ComplianceError):
    """A crawl was blocked by robots.txt."""


class Transport:
    """Minimal GET transport contract. Returns (status, content_type, body)."""

    def get(self, url: str) -> tuple[int, str, bytes]:  # pragma: no cover - protocol
        raise NotImplementedError


TransportGet = Callable[[str], tuple[int, str, bytes]]


class CompliantFetcher:
    def __init__(
        self,
        registry: SourceRegistry,
        transport: TransportGet,
        *,
        robots: RobotsPolicy | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._registry = registry
        self._transport = transport
        self._robots = robots
        self._clock = clock

    def fetch(self, url: str, *, source_name: str) -> RawArtifact:
        source = self._registry.require_allowed(url)  # raises if not allowlisted
        if source.kind == SourceKind.CRAWL and source.respect_robots:
            if self._robots is None:
                raise FetchBlockedError(
                    f"Crawl source {source.name!r} requires a robots policy but none was provided"
                )
            if not self._robots.can_fetch(url):
                raise FetchBlockedError(f"robots.txt disallows fetching {url!r}")
        status, content_type, body = self._transport(url)
        if status >= 400:
            raise FetchBlockedError(f"Fetch of {url!r} returned HTTP {status}")
        return RawArtifact(
            source=source_name,
            url=url,
            fetched_at=self._clock(),
            content_type=content_type,
            body=body,
        )
