"""Adapter contract: fetch (through the compliance gate) → raw artifact → normalize.

Adapters never fetch directly; they delegate to a CompliantFetcher, so the
allowed-sources + robots checks cannot be bypassed by a new adapter. `parse` turns
one artifact into candidate companies/signals and must not emit person data
(enforced downstream by normalize.build_signal).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from li_ingestion.artifacts import CandidateCompany, CandidateSignal, RawArtifact
from li_ingestion.fetcher import CompliantFetcher


@dataclass(frozen=True, slots=True)
class AdapterResult:
    companies: list[CandidateCompany] = field(default_factory=list)
    signals: list[CandidateSignal] = field(default_factory=list)


class Adapter(ABC):
    #: stable adapter name; used as the RawArtifact.source and the guard context.
    name: str

    def fetch(self, fetcher: CompliantFetcher, url: str) -> RawArtifact:
        return fetcher.fetch(url, source_name=self.name)

    @abstractmethod
    def parse(self, artifact: RawArtifact) -> AdapterResult: ...
