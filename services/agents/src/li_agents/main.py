"""Agents worker entrypoint.

The queue-worker wiring (claim companies, build the MeteredClient with the DB cost
sink and a real Anthropic client, persist scores) is joined when the pipeline runs
end-to-end. The passes and orchestration are pure over MeteredClient + ToolContext
and fully unit-tested against the stub LLM.
"""

from __future__ import annotations


def main() -> None:  # pragma: no cover - process entrypoint
    raise SystemExit("agents worker loop is wired in a later chunk")
