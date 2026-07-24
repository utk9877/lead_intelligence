"""Tests for the real-API normalization path — especially that thinking blocks are
preserved so the pass-2 tool loop can echo them back unchanged (else the API 400s)."""

from __future__ import annotations

from types import SimpleNamespace

from li_llm.client import _normalize


def _message(content: list[object], stop_reason: str = "tool_use") -> SimpleNamespace:
    return SimpleNamespace(
        content=content,
        model="claude-opus-4-8",
        stop_reason=stop_reason,
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=20,
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
        ),
    )


def test_thinking_block_preserved_before_tool_use() -> None:
    thinking = SimpleNamespace(type="thinking", thinking="reasoning...", signature="sig123")
    tool = SimpleNamespace(type="tool_use", id="toolu_1", name="graph_lookup", input={"x": 1})
    response = _normalize(_message([thinking, tool]))
    # The thinking block must be first and carry its signature verbatim, so the next
    # assistant turn round-trips it.
    assert response.raw_content[0] == {
        "type": "thinking",
        "thinking": "reasoning...",
        "signature": "sig123",
    }
    assert response.raw_content[1]["type"] == "tool_use"
    assert len(response.tool_calls) == 1


def test_redacted_thinking_preserved() -> None:
    redacted = SimpleNamespace(type="redacted_thinking", data="opaque-bytes")
    text = SimpleNamespace(type="text", text="hi")
    response = _normalize(_message([redacted, text], stop_reason="end_turn"))
    assert response.raw_content[0] == {"type": "redacted_thinking", "data": "opaque-bytes"}
    assert response.text == "hi"


def test_usage_mapped_from_sdk_fields() -> None:
    text = SimpleNamespace(type="text", text="x")
    response = _normalize(_message([text], stop_reason="end_turn"))
    assert response.usage.input_tokens == 10
    assert response.usage.output_tokens == 20
