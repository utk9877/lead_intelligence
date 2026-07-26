"""Claude client, model tiering, prompt caching, budget caps, cost ledger."""

from li_llm.budget import BudgetExceededError, BudgetGuard
from li_llm.client import AnthropicClient, LLMClient
from li_llm.ledger import CostEntry, CostSink, CostStage, InMemoryCostSink
from li_llm.metered import STAGE_TIER, MeteredClient
from li_llm.openai_client import OpenAICompatibleClient
from li_llm.prompt_cache import cached_system
from li_llm.stub import StubLLMClient, text_response
from li_llm.tiers import (
    DEFAULT_USD_TO_INR,
    MODEL_PRICING,
    TIER_MODELS,
    ModelTier,
    cost_inr,
    model_for,
    register_model_pricing,
)
from li_llm.types import LLMResponse, ToolCall, Usage

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_USD_TO_INR",
    "MODEL_PRICING",
    "STAGE_TIER",
    "TIER_MODELS",
    "AnthropicClient",
    "BudgetExceededError",
    "BudgetGuard",
    "CostEntry",
    "CostSink",
    "CostStage",
    "InMemoryCostSink",
    "LLMClient",
    "LLMResponse",
    "MeteredClient",
    "ModelTier",
    "OpenAICompatibleClient",
    "StubLLMClient",
    "ToolCall",
    "Usage",
    "cached_system",
    "cost_inr",
    "model_for",
    "register_model_pricing",
    "text_response",
]
