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


def _mrkdwn_escape(text: str) -> str:
    """Escape the three Slack mrkdwn control chars so agent/evidence free text can't
    inject links, @channel/@here broadcasts, or break the layout."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _safe_link(url: str, label: str) -> str:
    # A URL containing mrkdwn link delimiters can't be a safe <url|label>; degrade
    # to escaped plain text rather than emit a broken/injectable link.
    if any(c in url for c in "<>|"):
        return f"{_mrkdwn_escape(label)}: {_mrkdwn_escape(url)}"
    return f"<{url}|{_mrkdwn_escape(label)}>"


def card_to_blocks(card: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Render an account card as Slack Block Kit, one citation per claim."""
    header = f"{str(card['band']).upper()} · score {card['score']} — {card.get('company_id', '')}"
    blocks: list[dict[str, Any]] = [
        {"type": "header", "text": {"type": "plain_text", "text": header[:150]}},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Why now:* {_mrkdwn_escape(card['why_now'])}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Why fit:* {_mrkdwn_escape(card['why_fit'])}"},
        },
        {"type": "divider"},
    ]
    for claim in card["claims"]:
        text = f"• {_mrkdwn_escape(claim['text'])}  {_safe_link(claim['source_url'], 'source')}"
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
    return blocks


def deliver_to_slack(transport: SlackTransport, webhook_url: str, card: Mapping[str, Any]) -> None:
    status = transport(webhook_url, {"blocks": card_to_blocks(card)})
    if not 200 <= status < 300:
        raise SlackDeliveryError(f"Slack webhook returned HTTP {status}")
