"""THE allowed-sources registry — every fetcher must pass it (RISKS.md#data-tos as code).

The default registry ships EMPTY on purpose: no registry vendor is chosen yet
(QUESTIONS.md#api-vendor) and no crawl sources are approved yet. Because every
fetcher is required to call `require_allowed`, an empty registry means nothing can
be fetched until a source is added here deliberately, in code review.
"""

from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlsplit

from li_compliance.errors import DisallowedSourceError


class SourceKind(StrEnum):
    REGISTRY_API = "registry_api"
    CRAWL = "crawl"
    FEED = "feed"


@dataclass(frozen=True, slots=True)
class AllowedSource:
    name: str
    kind: SourceKind
    domains: tuple[str, ...]
    respect_robots: bool = True


class SourceRegistry:
    def __init__(self, sources: tuple[AllowedSource, ...] = ()) -> None:
        self._sources = sources

    @property
    def sources(self) -> tuple[AllowedSource, ...]:
        return self._sources

    def match(self, url: str) -> AllowedSource | None:
        host = urlsplit(url).hostname
        if host is None:
            return None
        host = host.lower()
        for source in self._sources:
            for domain in source.domains:
                domain = domain.lower()
                if host == domain or host.endswith("." + domain):
                    return source
        return None

    def is_allowed(self, url: str) -> bool:
        return self.match(url) is not None

    def require_allowed(self, url: str) -> AllowedSource:
        source = self.match(url)
        if source is None:
            raise DisallowedSourceError(
                f"Fetch blocked: {url!r} matches no entry in the allowed-sources "
                "registry (RISKS.md#data-tos). Add the source in code review or do "
                "not fetch it."
            )
        return source


# Deliberately empty until sources are approved (see module docstring).
DEFAULT_REGISTRY = SourceRegistry(())
