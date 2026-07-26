"""Delivery worker entrypoint.

Consumes QA-approved accounts, renders cards, delivers (Slack), records the
delivery, and later captures feedback — wired to the real queue + repositories when
the pipeline runs end-to-end. The rendering/Slack/reporting units are pure and
unit-tested; the full flow is exercised by the end-to-end smoke test.
"""

from __future__ import annotations


def main() -> None:  # pragma: no cover - process entrypoint
    raise SystemExit("delivery worker loop is wired in a later chunk")
