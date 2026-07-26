"""Translation tests for the OpenAI-compatible client (no network — fake transport)."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from li_llm.openai_client import OpenAICompatibleClient


def _client(
    responder: Callable[[dict[str, Any]], dict[str, Any]], captured: list[dict[str, Any]]
) -> OpenAICompatibleClient:
    def transport(url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
        captured.append(body)
        return responder(body)

    return OpenAICompatibleClient(
        base_url="https://api.groq.test/openai/v1",
        api_key="k",
        model="llama-3.3-70b",
        transport=transport,
    )


def test_text_completion_round_trip() -> None:
    captured: list[dict[str, Any]] = []
    client = _client(
        lambda _b: {
            "model": "llama-3.3-70b",
            "choices": [{"message": {"content": '{"ok": true}'}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 8},
        },
        captured,
    )
    resp = client.create(
        model="claude-haiku-4-5",
        system="be terse",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=100,
    )
    assert resp.text == '{"ok": true}'
    assert resp.stop_reason == "end_turn"
    assert resp.usage.input_tokens == 12 and resp.usage.output_tokens == 8
    # System became an OpenAI system message; the configured model was used.
    assert captured[0]["model"] == "llama-3.3-70b"
    assert captured[0]["messages"][0] == {"role": "system", "content": "be terse"}


def test_tool_call_translation_both_directions() -> None:
    captured: list[dict[str, Any]] = []
    client = _client(
        lambda _b: {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": "graph_lookup",
                                    "arguments": '{"company_id": "x"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 2},
        },
        captured,
    )
    tools = [
        {
            "name": "graph_lookup",
            "description": "d",
            "input_schema": {"type": "object", "properties": {}},
        }
    ]
    resp = client.create(
        model="claude-opus-4-8",
        system="s",
        messages=[{"role": "user", "content": "go"}],
        max_tokens=100,
        tools=tools,
    )
    # Response → our ToolCall + tool_use stop reason.
    assert resp.stop_reason == "tool_use"
    assert resp.tool_calls[0].name == "graph_lookup"
    assert resp.tool_calls[0].input == {"company_id": "x"}
    # Request → OpenAI function-tool shape.
    assert captured[0]["tools"][0]["type"] == "function"
    assert captured[0]["tools"][0]["function"]["name"] == "graph_lookup"


def test_tool_loop_history_translates() -> None:
    # The harness re-sends assistant tool_use + user tool_result blocks; they must
    # translate to OpenAI assistant.tool_calls + role:tool messages.
    captured: list[dict[str, Any]] = []
    client = _client(
        lambda _b: {
            "choices": [{"message": {"content": '{"done": 1}'}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        },
        captured,
    )
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": "research"},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "let me look"},
                {"type": "tool_use", "id": "call_1", "name": "graph_lookup", "input": {"x": 1}},
            ],
        },
        {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "call_1", "content": "{}"}],
        },
    ]
    client.create(model="claude-opus-4-8", system="s", messages=messages, max_tokens=100)
    sent = captured[0]["messages"]
    assistant = next(m for m in sent if m["role"] == "assistant")
    assert assistant["tool_calls"][0]["id"] == "call_1"
    assert json.loads(assistant["tool_calls"][0]["function"]["arguments"]) == {"x": 1}
    tool_msg = next(m for m in sent if m["role"] == "tool")
    assert tool_msg["tool_call_id"] == "call_1"
