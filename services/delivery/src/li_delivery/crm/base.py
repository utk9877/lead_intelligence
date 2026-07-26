from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from li_core.errors import LeadIntelligenceError


class CrmNotConfiguredError(LeadIntelligenceError):
    """A CRM integration was invoked before it was implemented/configured (P2)."""


@runtime_checkable
class CrmSync(Protocol):
    def push_account(self, card: Mapping[str, Any]) -> str:
        """Push a delivered account card into the CRM; returns the CRM record id."""
        ...
