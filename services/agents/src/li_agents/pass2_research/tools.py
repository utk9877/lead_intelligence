"""Tools the research pass can call, and their execution context.

Every tool implementation is injected (a callable), so the harness is testable
without a database, object store, or network. `site_fetch` in production is wired
to go through the li-compliance gate (RISKS.md#data-tos); here it is just a seam.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from li_agents.parsing import ModelOutputError

# JSON-schema tool definitions passed to the model.
TOOL_DEFS: list[dict[str, Any]] = [
    {
        "name": "graph_lookup",
        "description": "Fetch stored company-graph facts (signals, identifiers) by company id.",
        "input_schema": {
            "type": "object",
            "properties": {"company_id": {"type": "string"}},
            "required": ["company_id"],
        },
    },
    {
        "name": "site_fetch",
        "description": "Fetch a company site page (through the compliance gate).",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "registry_fetch",
        "description": "Fetch registry (MCA/GST) facts by CIN or GSTIN.",
        "input_schema": {
            "type": "object",
            "properties": {"identifier": {"type": "string"}},
            "required": ["identifier"],
        },
    },
    {
        "name": "snapshot_read",
        "description": "Read a stored evidence snapshot by its key.",
        "input_schema": {
            "type": "object",
            "properties": {"snapshot_key": {"type": "string"}},
            "required": ["snapshot_key"],
        },
    },
]

_TOOL_NAMES = frozenset(t["name"] for t in TOOL_DEFS)

Handler = Callable[[Mapping[str, Any]], str]


@dataclass
class ToolContext:
    graph_lookup: Handler
    site_fetch: Handler
    registry_fetch: Handler
    snapshot_read: Handler

    def handler(self, name: str) -> Handler:
        if name not in _TOOL_NAMES:
            raise ModelOutputError(f"model called unknown tool {name!r}")
        return getattr(self, name)  # type: ignore[no-any-return]
