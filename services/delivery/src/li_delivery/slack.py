"""Slack delivery via incoming webhook.

The HTTP transport is injected so tests never touch the network. The card is
rendered into Slack Block Kit; the webhook URL is a secret held by the caller.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from li_core.errors import LeadIntelligenceError

# Transport: given (url, json_body) -> status code. Injected for testability.
SlackTransport = Callable[[str, dict[str, Any]], int]


class SlackDeliveryError(LeadIntelligenceError):
    """Slack returned a non-2xx response."""


def card_to_blocks(card: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Render an account card as Slack Block Kit, one citation per claim."""
    header = f"{str(card['band']).upper()} · score {card['score']} — {card.get('company_id', '')}"
    blocks: list[dict[str, Any]] = [
        {"type": "header", "text": {"type": "plain_text", "text": header[:150]}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Why now:* {card['why_now']}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Why fit:* {card['why_fit']}"}},
        {"type": "divider"},
    ]
    for claim in card["claims"]:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• {claim['text']}  <{claim['source_url']}|source>",
                },
            }
        )
    return blocks


def deliver_to_slack(transport: SlackTransport, webhook_url: str, card: Mapping[str, Any]) -> None:
    status = transport(webhook_url, {"blocks": card_to_blocks(card)})
    if not 200 <= status < 300:
        raise SlackDeliveryError(f"Slack webhook returned HTTP {status}")
