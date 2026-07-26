"""MeteredClient: the seam every pass calls through.

It maps a pass to its model tier, runs the call, prices the usage, records a cost
ledger row, and charges the per-account budget (which raises to kill a runaway
loop). Nothing in the agent pipeline calls an LLM except through this.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from li_llm.budget import BudgetGuard
from li_llm.client import LLMClient
from li_llm.ledger import CostEntry, CostSink, CostStage
from li_llm.tiers import DEFAULT_USD_TO_INR, MODEL_PRICING, ModelTier, cost_inr, model_for
from li_llm.types import LLMResponse

# Which model tier each cost stage runs on (single source of truth).
STAGE_TIER: dict[CostStage, ModelTier] = {
    CostStage.PASS1_TRIGGERS: ModelTier.SMALL,
    CostStage.PASS2_RESEARCH: ModelTier.FRONTIER,
    CostStage.PASS3_SCORING: ModelTier.MID,
}


class MeteredClient:
    def __init__(
        self,
        client: LLMClient,
        sink: CostSink,
        *,
        budget: BudgetGuard | None = None,
        customer_id: uuid.UUID | None = None,
        company_id: uuid.UUID | None = None,
        provider: str = "anthropic",
        usd_to_inr: Decimal = DEFAULT_USD_TO_INR,
    ) -> None:
        self._client = client
        self._sink = sink
        self._budget = budget
        self._customer_id = customer_id
        self._company_id = company_id
        self._provider = provider
        self._usd_to_inr = usd_to_inr

    def run(
        self,
        *,
        stage: CostStage,
        system: str | list[dict[str, Any]],
        messages: list[dict[str, Any]],
        max_tokens: int,
        tools: Sequence[dict[str, Any]] | None = None,
        thinking: bool = False,
        effort: str | None = None,
    ) -> LLMResponse:
        model = model_for(STAGE_TIER[stage])
        response = self._client.create(
            model=model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            tools=tools,
            thinking=thinking,
            effort=effort,
        )
        # Price on the model the response reports IF it has pricing (so an
        # open-source model behind an OpenAI-compatible endpoint prices correctly);
        # otherwise fall back to the requested tier model. A stub's unpriced
        # "stub-model" falls back to the Anthropic tier model as before.
        priced_model = response.model if response.model in MODEL_PRICING else model
        try:
            cost = cost_inr(priced_model, response.usage, usd_to_inr=self._usd_to_inr)
        except KeyError:
            cost = Decimal("0")  # unknown model: record the call, price it 0
        self._sink.record(
            CostEntry(
                stage=stage,
                provider=self._provider,
                model=priced_model,
                cost_inr=cost,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                company_id=self._company_id,
                customer_id=self._customer_id,
                meta={"stop_reason": response.stop_reason},
            )
        )
        # Record first, then charge — so the ledger captures the call that trips the
        # cap before this raises and aborts the pass.
        if self._budget is not None:
            self._budget.charge(cost)
        return response
