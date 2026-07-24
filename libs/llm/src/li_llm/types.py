"""Normalized request/response types, provider-agnostic.

The stub client and the Anthropic client both speak these, so the whole agent
pipeline is testable in CI without an API key or network.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    name: str
    input: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class LLMResponse:
    model: str
    stop_reason: str  # "end_turn" | "tool_use" | "max_tokens" | "refusal" | ...
    text: str
    tool_calls: Sequence[ToolCall]
    usage: Usage
    # The assistant turn's content blocks verbatim, to append back into a tool loop.
    raw_content: list[dict[str, Any]] = field(default_factory=list)
