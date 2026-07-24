from decimal import Decimal

import pytest
from li_llm.tiers import (
    MODEL_PRICING,
    TIER_MODELS,
    ModelTier,
    cost_inr,
    model_for,
)
from li_llm.types import Usage


def test_every_tier_maps_to_a_priced_model() -> None:
    for tier in ModelTier:
        model = model_for(tier)
        assert model in MODEL_PRICING, f"{tier} → {model} has no pricing"


def test_tier_model_ids_are_exact() -> None:
    assert TIER_MODELS[ModelTier.SMALL] == "claude-haiku-4-5"
    assert TIER_MODELS[ModelTier.MID] == "claude-sonnet-5"
    assert TIER_MODELS[ModelTier.FRONTIER] == "claude-opus-4-8"


def test_cost_of_one_million_input_tokens_is_list_price_times_fx() -> None:
    # Haiku input is $1.00/1M; at ₹83/$ that's ₹83 for 1M input tokens.
    cost = cost_inr("claude-haiku-4-5", Usage(input_tokens=1_000_000))
    assert cost == Decimal("83.0")


def test_output_priced_higher_than_input() -> None:
    in_cost = cost_inr("claude-opus-4-8", Usage(input_tokens=1000))
    out_cost = cost_inr("claude-opus-4-8", Usage(output_tokens=1000))
    assert out_cost == in_cost * 5  # Opus output is 5x input


def test_cache_read_is_cheaper_than_fresh_input() -> None:
    fresh = cost_inr("claude-sonnet-5", Usage(input_tokens=10_000))
    cached = cost_inr("claude-sonnet-5", Usage(cache_read_tokens=10_000))
    assert cached == fresh / 10  # cache read ~0.1x


def test_unknown_model_raises() -> None:
    with pytest.raises(KeyError):
        cost_inr("gpt-4", Usage(input_tokens=1))
