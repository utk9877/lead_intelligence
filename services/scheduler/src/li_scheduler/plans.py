"""Refresh planning: decide which (company, source) pairs are due for a re-fetch.

Pure and deterministic — given the current time, per-source cadences, and each
target's last-refresh time, it returns the due jobs. No I/O, so it is fully
unit-testable; the worker (main.py) supplies real state and enqueues the result.
At P1 this runs from host cron (docs/ARCHITECTURE.md §11) — no leader election yet.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

# Default per-source cadence. Registry data changes slowly; news/careers fast.
DEFAULT_CADENCE: Mapping[str, timedelta] = {
    "registry_mca": timedelta(days=30),
    "registry_gst": timedelta(days=30),
    "news_funding": timedelta(days=1),
    "careers_pages": timedelta(days=3),
    "job_boards": timedelta(days=3),
    "site_tech": timedelta(days=14),
}


@dataclass(frozen=True, slots=True)
class RefreshTarget:
    company_id: str
    source: str
    url: str
    last_refreshed: datetime | None  # None = never fetched


@dataclass(frozen=True, slots=True)
class RefreshJob:
    company_id: str
    source: str
    url: str


def due_jobs(
    targets: Iterable[RefreshTarget],
    *,
    now: datetime,
    cadence: Mapping[str, timedelta] = DEFAULT_CADENCE,
) -> list[RefreshJob]:
    now = _as_utc(now)
    jobs: list[RefreshJob] = []
    for target in targets:
        interval = cadence.get(target.source)
        if interval is None:
            # Unknown source: never schedule blindly — must be configured explicitly.
            continue
        last = None if target.last_refreshed is None else _as_utc(target.last_refreshed)
        if last is None or now - last >= interval:
            jobs.append(
                RefreshJob(company_id=target.company_id, source=target.source, url=target.url)
            )
    return jobs


def _as_utc(value: datetime) -> datetime:
    """Treat a naive datetime as UTC (our DB stores tz-aware UTC) so mixing a naive
    last_refreshed with an aware `now` can never raise a subtraction TypeError."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
