"""CRM sync — stubbed at the interface. Automated sync is a P2 item (§11).

The protocol is defined now so delivery code can target it; HubSpot/Zoho
implementations raise until a customer needs them, so a stub is never silently
mistaken for a real integration.
"""

from li_delivery.crm.base import CrmNotConfiguredError, CrmSync
from li_delivery.crm.hubspot import HubSpotSync
from li_delivery.crm.zoho import ZohoSync

__all__ = ["CrmNotConfiguredError", "CrmSync", "HubSpotSync", "ZohoSync"]
