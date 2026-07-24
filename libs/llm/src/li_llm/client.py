"""LLM client protocol + the Anthropic implementation.

The protocol is the seam docs/ARCHITECTURE.md §7 calls out: swapping the direct
Anthropic API for Bedrock (or a stub in tests) happens here and nowhere else.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable

from li_llm.types import LLMResponse, ToolCall, Usage


@runtime_checkable
class LLMClient(Protocol):
    def create(
        self,
        *,
        model: str,
        system: str | list[dict[str, Any]],
        messages: list[dict[str, Any]],
        max_tokens: int,
        tools: Sequence[dict[str, Any]] | None = None,
        thinking: bool = False,
        effort: str | None = None,
    ) -> LLMResponse: ...


class AnthropicClient:
    """Wraps the Anthropic SDK. Adaptive thinking and effort are set explicitly
    (never sampling params — Opus 4.8 / Sonnet 5 reject temperature/top_p)."""

    def __init__(self, sdk_client: Any) -> None:
        # `sdk_client` is an anthropic.Anthropic instance; injected so construction
        # (and API-key resolution) stays out of this module.
        self._client = sdk_client

    def create(
        self,
        *,
        model: str,
        system: str | list[dict[str, Any]],
        messages: list[dict[str, Any]],
        max_tokens: int,
        tools: Sequence[dict[str, Any]] | None = None,
        thinking: bool = False,
        effort: str | None = None,
    ) -> LLMResponse:  # pragma: no cover - exercised only against the real API
        kwargs: dict[str, Any] = {
            "model": model,
            "system": system,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = list(tools)
        if thinking:
            kwargs["thinking"] = {"type": "adaptive"}
        output_config: dict[str, Any] = {}
        if effort is not None:
            output_config["effort"] = effort
        if output_config:
            kwargs["output_config"] = output_config

        message = self._client.messages.create(**kwargs)
        return _normalize(message)


def _normalize(message: Any) -> LLMResponse:  # pragma: no cover - real-API shape
    text_parts: list[str] = []
    tool_calls: list[ToolCall] = []
    raw_content: list[dict[str, Any]] = []
    for block in message.content:
        block_type = getattr(block, "type", None)
        if block_type == "text":
            text_parts.append(block.text)
            raw_content.append({"type": "text", "text": block.text})
        elif block_type == "tool_use":
            tool_calls.append(ToolCall(id=block.id, name=block.name, input=block.input))
            raw_content.append(
                {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
            )
    usage = Usage(
        input_tokens=getattr(message.usage, "input_tokens", 0) or 0,
        output_tokens=getattr(message.usage, "output_tokens", 0) or 0,
        cache_read_tokens=getattr(message.usage, "cache_read_input_tokens", 0) or 0,
        cache_write_tokens=getattr(message.usage, "cache_creation_input_tokens", 0) or 0,
    )
    return LLMResponse(
        model=message.model,
        stop_reason=message.stop_reason,
        text="".join(text_parts),
        tool_calls=tool_calls,
        usage=usage,
        raw_content=raw_content,
    )
