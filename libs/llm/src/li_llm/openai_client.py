"""OpenAI-compatible client — for open-source models (Groq, OpenRouter, Together,
Fireworks, DeepSeek, Ollama, vLLM, …), which all speak the OpenAI chat-completions
API rather than Anthropic's.

It conforms to the same LLMClient protocol as AnthropicClient, translating the
Anthropic-shaped request (system / messages / tools, including the pass-2 tool-use
loop) to OpenAI format and the response back. adaptive-thinking / effort are
Anthropic-only and are ignored here. The HTTP transport is injectable so the
translation is unit-tested without a network.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import Any

from li_llm.types import LLMResponse, ToolCall, Usage

# Transport: (url, headers, json_body) -> parsed JSON dict. Injected for testing.
HttpPost = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]

_FINISH_TO_STOP = {"stop": "end_turn", "tool_calls": "tool_use", "length": "max_tokens"}


class OpenAICompatibleClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        transport: HttpPost | None = None,
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._transport = transport
        self._timeout = timeout

    def create(
        self,
        *,
        model: str,  # tier model (ignored — this client uses its configured model)
        system: str | list[dict[str, Any]],
        messages: list[dict[str, Any]],
        max_tokens: int,
        tools: Sequence[dict[str, Any]] | None = None,
        thinking: bool = False,  # Anthropic-only, ignored
        effort: str | None = None,  # Anthropic-only, ignored
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": _to_openai_messages(system, messages),
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = _to_openai_tools(tools)
        data = self._post("/chat/completions", payload)
        return _parse_response(data, fallback_model=self._model)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = self._base_url + path
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "content-type": "application/json",
        }
        if self._transport is not None:
            return self._transport(url, headers, payload)
        import httpx  # pragma: no cover - real network path

        response = httpx.post(url, headers=headers, json=payload, timeout=self._timeout)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result


def _to_openai_tools(tools: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


def _to_openai_messages(
    system: str | list[dict[str, Any]], messages: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    system_text = (
        system if isinstance(system, str) else "\n".join(b.get("text", "") for b in system)
    )
    if system_text:
        out.append({"role": "system", "content": system_text})

    for message in messages:
        role = message["role"]
        content = message["content"]
        if isinstance(content, str):
            out.append({"role": role, "content": content})
            continue
        # content is a list of Anthropic-style blocks.
        if role == "assistant":
            out.append(_assistant_blocks_to_openai(content))
        else:  # user turn carrying tool_result blocks (and/or text)
            out.extend(_user_blocks_to_openai(content))
    return out


def _assistant_blocks_to_openai(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    for block in blocks:
        if block["type"] == "text":
            text_parts.append(block["text"])
        elif block["type"] == "tool_use":
            tool_calls.append(
                {
                    "id": block["id"],
                    "type": "function",
                    "function": {"name": block["name"], "arguments": json.dumps(block["input"])},
                }
            )
        # thinking / redacted_thinking blocks have no OpenAI equivalent — drop them.
    message: dict[str, Any] = {"role": "assistant", "content": "".join(text_parts) or None}
    if tool_calls:
        message["tool_calls"] = tool_calls
    return message


def _user_blocks_to_openai(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for block in blocks:
        if block["type"] == "tool_result":
            out.append(
                {
                    "role": "tool",
                    "tool_call_id": block["tool_use_id"],
                    "content": block["content"],
                }
            )
        elif block["type"] == "text":
            out.append({"role": "user", "content": block["text"]})
    return out


def _parse_response(data: dict[str, Any], *, fallback_model: str) -> LLMResponse:
    choice = data["choices"][0]
    message = choice.get("message", {})
    text = message.get("content") or ""
    tool_calls: list[ToolCall] = []
    raw_content: list[dict[str, Any]] = []
    if text:
        raw_content.append({"type": "text", "text": text})
    for tc in message.get("tool_calls") or []:
        args = json.loads(tc["function"].get("arguments") or "{}")
        tool_calls.append(ToolCall(id=tc["id"], name=tc["function"]["name"], input=args))
        raw_content.append(
            {"type": "tool_use", "id": tc["id"], "name": tc["function"]["name"], "input": args}
        )
    usage_raw = data.get("usage") or {}
    usage = Usage(
        input_tokens=usage_raw.get("prompt_tokens", 0) or 0,
        output_tokens=usage_raw.get("completion_tokens", 0) or 0,
    )
    stop_reason = _FINISH_TO_STOP.get(choice.get("finish_reason", "stop"), "end_turn")
    return LLMResponse(
        model=data.get("model", fallback_model),
        stop_reason=stop_reason,
        text=text,
        tool_calls=tool_calls,
        usage=usage,
        raw_content=raw_content,
    )
