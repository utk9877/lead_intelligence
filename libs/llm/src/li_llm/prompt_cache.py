"""Prompt-cache helpers.

The stable per-customer ICP preamble is the cacheable prefix (docs/ARCHITECTURE.md
§3). Keep volatile per-account content OUT of the cached block or the prefix match
breaks and nothing caches.
"""

from __future__ import annotations

from typing import Any


def cached_system(text: str) -> list[dict[str, Any]]:
    """A single cached system block. Use for the frozen customer-ICP preamble;
    put per-account facts in the user turn, never here."""
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]
