"""The compliance gate every fetch passes through (docs/ARCHITECTURE.md §1, RISKS.md#data-tos).

Before any byte is fetched from a host, that host is checked:
  1. `allowed_sources.require_allowed(url)` — unlisted host → DisallowedSourceError.
  2. For crawl sources honoring robots, `robots.can_fetch(url)` — blocked → FetchBlockedError.

Redirects are followed **by the fetcher, one hop at a time**, so every hop's target is
re-validated by the two checks above *before* it is fetched. The transport itself must
NOT follow redirects — otherwise it would contact a redirect target off the allowlist
before the gate could see it. The recorded artifact URL is the final hop, so evidence
cites the host the bytes actually came from.

The HTTP transport is injected so tests never touch the network. There is no code path
that fetches a host without passing the registry check for that exact host first.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from urllib.parse import urljoin

from li_compliance.allowed_sources import AllowedSource, SourceKind, SourceRegistry
from li_compliance.errors import ComplianceError
from li_compliance.robots import RobotsPolicy

from li_ingestion.artifacts import RawArtifact

_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_MAX_REDIRECTS = 5


class FetchBlockedError(ComplianceError):
    """A crawl was blocked by robots.txt, an HTTP error, or a redirect limit."""


# Transport contract: given a URL, return (status, content_type, body, location).
# It MUST NOT follow redirects — on a 3xx it returns the Location header as the
# fourth element (None otherwise). The fetcher decides whether to follow.
TransportGet = Callable[[str], tuple[int, str, bytes, "str | None"]]


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

    def _gate(self, url: str) -> AllowedSource:
        """Both compliance checks for one host; raises before the host is contacted."""
        source = self._registry.require_allowed(url)  # unlisted host → raises
        if source.kind == SourceKind.CRAWL and source.respect_robots:
            if self._robots is None:
                raise FetchBlockedError(
                    f"Crawl source {source.name!r} requires a robots policy but none was provided"
                )
            if not self._robots.can_fetch(url):
                raise FetchBlockedError(f"robots.txt disallows fetching {url!r}")
        return source

    def fetch(self, url: str, *, source_name: str) -> RawArtifact:
        current = url
        for _ in range(_MAX_REDIRECTS + 1):
            self._gate(current)  # validate THIS host before contacting it
            status, content_type, body, location = self._transport(current)
            if status in _REDIRECT_STATUSES and location is not None:
                current = urljoin(current, location)
                continue  # loop re-gates the redirect target before following it
            if status >= 400:
                raise FetchBlockedError(f"Fetch of {current!r} returned HTTP {status}")
            return RawArtifact(
                source=source_name,
                url=current,  # final hop — evidence cites where the bytes came from
                fetched_at=self._clock(),
                content_type=content_type,
                body=body,
            )
        raise FetchBlockedError(f"Too many redirects fetching {url!r} (>{_MAX_REDIRECTS})")
