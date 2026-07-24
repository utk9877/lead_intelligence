"""Parse the JSON payload out of a model response, tolerating ```json fences."""

from __future__ import annotations

import json
import re
from typing import Any

from li_core.errors import LeadIntelligenceError

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


class ModelOutputError(LeadIntelligenceError):
    """The model's response was not the JSON the pass required."""


def parse_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    match = _FENCE.search(candidate)
    if match:
        candidate = match.group(1).strip()
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise ModelOutputError(f"expected JSON, got: {text[:200]!r}") from error
    if not isinstance(data, dict):
        raise ModelOutputError(f"expected a JSON object, got {type(data).__name__}")
    return data
