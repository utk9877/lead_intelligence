from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from li_delivery.crm.base import CrmNotConfiguredError


class HubSpotSync:
    """Interface-conformant stub — automated CRM sync activates at P2 (§11)."""

    def push_account(self, card: Mapping[str, Any]) -> str:
        raise CrmNotConfiguredError("HubSpot sync is not implemented until the P2 gate")
