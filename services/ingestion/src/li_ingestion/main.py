"""Ingestion worker entrypoint.

Chunk 2 wires the compliant HTTP transport and leaves queue-worker registration
for chunk 3+ (when the resolver consumes candidates). The network transport is
isolated here so the pipeline/adapters stay unit-testable without it.
"""

from __future__ import annotations

import httpx

from li_ingestion.fetcher import TransportGet


def httpx_transport(timeout: float = 20.0, user_agent: str = "li-bot/0.1") -> TransportGet:
    client = httpx.Client(
        timeout=timeout, headers={"User-Agent": user_agent}, follow_redirects=True
    )

    def get(url: str) -> tuple[int, str, bytes]:  # pragma: no cover - network
        response = client.get(url)
        return (
            response.status_code,
            response.headers.get("content-type", "application/octet-stream"),
            response.content,
        )

    return get


def main() -> None:  # pragma: no cover - process entrypoint
    raise SystemExit("ingestion worker loop is wired in a later chunk")
