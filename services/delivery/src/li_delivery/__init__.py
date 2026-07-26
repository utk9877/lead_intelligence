"""Account cards, Slack delivery, CRM stubs, cost reporting.

Feedback capture (customer pursue/reject → the deliveries table) lives in
li-db's DeliveryRepository — the labelled data the precision metric learns from.
"""

from li_delivery.cards import NotDeliverableError, render_delivery_card
from li_delivery.reporting import format_cost_report
from li_delivery.slack import SlackDeliveryError, card_to_blocks, deliver_to_slack

__version__ = "0.1.0"

__all__ = [
    "NotDeliverableError",
    "SlackDeliveryError",
    "card_to_blocks",
    "deliver_to_slack",
    "format_cost_report",
    "render_delivery_card",
]
