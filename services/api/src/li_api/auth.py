"""Internal API-key auth (QA console → api).

Simple shared-key gate for P1/P2 — the console is the only client and both run
inside the same trust boundary. Customer-facing auth is a P3 concern (§11).
"""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status
from li_core.config import get_settings

_API_KEY_HEADER = "x-api-key"


def require_api_key(x_api_key: str = Header(default="", alias=_API_KEY_HEADER)) -> None:
    expected = get_settings().internal_api_key
    # Constant-time compare to avoid a timing side-channel on the shared key.
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key"
        )
