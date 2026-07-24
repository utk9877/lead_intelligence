"""Resolver worker entrypoint.

The queue-worker wiring (consume candidates from ingestion, resolve, persist) lands
when the pipeline is joined end-to-end. The resolution logic in resolve.py is pure
over the repositories and fully unit-tested without a worker loop.
"""

from __future__ import annotations


def main() -> None:  # pragma: no cover - process entrypoint
    raise SystemExit("resolver worker loop is wired in a later chunk")
