"""Model tiering and cost computation — the ONE place pass→model mapping lives.

Changing which model a pass uses is a one-line edit here (docs/ARCHITECTURE.md §2).
Pricing is public list price (USD per 1M tokens); the cost ledger records ₹, so a
USD→INR rate is applied. That rate is a *placeholder* like all economics in this
repo — it is configurable and must be treated as illustrative, not committed.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from li_llm.types import Usage


class ModelTier(StrEnum):
    SMALL = "small"  # pass 1 trigger classification — cheap, batched
    MID = "mid"  # pass 3 rubric scoring
    FRONTIER = "frontier"  # pass 2 deep-fit research (tool loop)


# Exact model IDs (never date-suffixed). Current Claude model line.
TIER_MODELS: dict[ModelTier, str] = {
    ModelTier.SMALL: "claude-haiku-4-5",
    ModelTier.MID: "claude-sonnet-5",
    ModelTier.FRONTIER: "claude-opus-4-8",
}


@dataclass(frozen=True, slots=True)
class ModelPricing:
    """USD per 1M tokens. Cache reads ~0.1x input; cache writes ~1.25x input."""

    input_per_mtok: Decimal
    output_per_mtok: Decimal

    @property
    def cache_read_per_mtok(self) -> Decimal:
        return self.input_per_mtok * Decimal("0.1")

    @property
    def cache_write_per_mtok(self) -> Decimal:
        return self.input_per_mtok * Decimal("1.25")


MODEL_PRICING: dict[str, ModelPricing] = {
    "claude-haiku-4-5": ModelPricing(Decimal("1.00"), Decimal("5.00")),
    "claude-sonnet-5": ModelPricing(Decimal("3.00"), Decimal("15.00")),
    "claude-opus-4-8": ModelPricing(Decimal("5.00"), Decimal("25.00")),
}


def register_model_pricing(model: str, input_per_mtok: Decimal, output_per_mtok: Decimal) -> None:
    """Register list pricing for a model not built in (e.g. an open-source model
    behind an OpenAI-compatible endpoint), so the cost ledger prices it correctly."""
    MODEL_PRICING[model] = ModelPricing(input_per_mtok, output_per_mtok)


# Placeholder FX rate — illustrative, configurable, never a commitment.
DEFAULT_USD_TO_INR = Decimal("83.0")

_PER_MTOK = Decimal("1000000")


def model_for(tier: ModelTier) -> str:
    return TIER_MODELS[tier]


def cost_inr(model: str, usage: Usage, *, usd_to_inr: Decimal = DEFAULT_USD_TO_INR) -> Decimal:
    """Cost of one call in ₹, from token usage and list price."""
    pricing = MODEL_PRICING.get(model)
    if pricing is None:
        raise KeyError(f"no pricing registered for model {model!r}")
    usd = (
        pricing.input_per_mtok * usage.input_tokens
        + pricing.output_per_mtok * usage.output_tokens
        + pricing.cache_read_per_mtok * usage.cache_read_tokens
        + pricing.cache_write_per_mtok * usage.cache_write_tokens
    ) / _PER_MTOK
    return usd * usd_to_inr
