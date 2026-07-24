"""Deterministic stub client for CI: canned responses, no network, no API key.

Two modes: a fixed queue of responses (popped per call), or a responder callable
that builds a response from the request. Every call is recorded for assertions.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from li_llm.types import LLMResponse, Usage


class StubLLMClient:
    def __init__(
        self,
        responses: Sequence[LLMResponse] | None = None,
        responder: Callable[[dict[str, Any]], LLMResponse] | None = None,
    ) -> None:
        if (responses is None) == (responder is None):
            raise ValueError("provide exactly one of responses or responder")
        self._queue = list(responses) if responses is not None else None
        self._responder = responder
        self.calls: list[dict[str, Any]] = []

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
    ) -> LLMResponse:
        request: dict[str, Any] = {
            "model": model,
            "system": system,
            "messages": messages,
            "max_tokens": max_tokens,
            "tools": list(tools) if tools else None,
            "thinking": thinking,
            "effort": effort,
        }
        self.calls.append(request)
        if self._responder is not None:
            return self._responder(request)
        assert self._queue is not None
        if not self._queue:
            raise AssertionError("StubLLMClient ran out of scripted responses")
        return self._queue.pop(0)


def text_response(
    text: str,
    *,
    model: str = "stub-model",
    input_tokens: int = 100,
    output_tokens: int = 50,
    stop_reason: str = "end_turn",
) -> LLMResponse:
    return LLMResponse(
        model=model,
        stop_reason=stop_reason,
        text=text,
        tool_calls=[],
        usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
        raw_content=[{"type": "text", "text": text}],
    )
