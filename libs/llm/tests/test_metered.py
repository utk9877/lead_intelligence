import uuid
from decimal import Decimal

import pytest
from li_llm.budget import BudgetExceededError, BudgetGuard
from li_llm.ledger import CostStage, InMemoryCostSink
from li_llm.metered import MeteredClient
from li_llm.stub import StubLLMClient, text_response
from li_llm.types import LLMResponse, Usage


def test_run_records_ledger_row_with_attribution() -> None:
    company, customer = uuid.uuid4(), uuid.uuid4()
    stub = StubLLMClient([text_response("ok", input_tokens=1_000_000, output_tokens=0)])
    sink = InMemoryCostSink()
    metered = MeteredClient(stub, sink, company_id=company, customer_id=customer)

    metered.run(stage=CostStage.PASS1_TRIGGERS, system="s", messages=[], max_tokens=10)

    assert len(sink.entries) == 1
    entry = sink.entries[0]
    assert entry.stage is CostStage.PASS1_TRIGGERS
    assert entry.model == "claude-haiku-4-5"  # SMALL tier for pass 1
    assert entry.company_id == company and entry.customer_id == customer
    assert entry.cost_inr == Decimal("83.0")  # 1M haiku input tokens


def test_pass_uses_the_right_tier_model() -> None:
    stub = StubLLMClient([text_response("x"), text_response("y"), text_response("z")])
    sink = InMemoryCostSink()
    metered = MeteredClient(stub, sink)
    metered.run(stage=CostStage.PASS1_TRIGGERS, system="s", messages=[], max_tokens=10)
    metered.run(stage=CostStage.PASS2_RESEARCH, system="s", messages=[], max_tokens=10)
    metered.run(stage=CostStage.PASS3_SCORING, system="s", messages=[], max_tokens=10)
    assert [c["model"] for c in stub.calls] == [
        "claude-haiku-4-5",
        "claude-opus-4-8",
        "claude-sonnet-5",
    ]


def test_budget_cap_kills_the_loop_and_ledger_keeps_the_breaching_call() -> None:
    # Each call costs ₹83 (1M haiku input); a ₹100 cap trips on the 2nd call.
    def big(_: object) -> LLMResponse:
        return text_response("x", input_tokens=1_000_000, output_tokens=0)

    stub = StubLLMClient(responder=big)
    sink = InMemoryCostSink()
    metered = MeteredClient(stub, sink, budget=BudgetGuard(Decimal("100")))

    metered.run(stage=CostStage.PASS1_TRIGGERS, system="s", messages=[], max_tokens=10)
    with pytest.raises(BudgetExceededError):
        metered.run(stage=CostStage.PASS1_TRIGGERS, system="s", messages=[], max_tokens=10)

    # Both calls were recorded — the ledger captures the account that breached.
    assert len(sink.entries) == 2
    assert sink.total_inr() == Decimal("166.0")


def test_effort_and_thinking_forwarded_but_no_sampling_params() -> None:
    stub = StubLLMClient([text_response("x")])
    metered = MeteredClient(stub, InMemoryCostSink())
    metered.run(
        stage=CostStage.PASS2_RESEARCH,
        system="s",
        messages=[],
        max_tokens=10,
        thinking=True,
        effort="high",
    )
    call = stub.calls[0]
    assert call["thinking"] is True
    assert call["effort"] == "high"
    # Sampling params are never part of the interface (Opus 4.8 rejects them).
    assert "temperature" not in call and "top_p" not in call


def test_usage_tokens_flow_to_ledger() -> None:
    stub = StubLLMClient(
        [LLMResponse("m", "end_turn", "t", [], Usage(input_tokens=12, output_tokens=34))]
    )
    sink = InMemoryCostSink()
    MeteredClient(stub, sink).run(
        stage=CostStage.PASS3_SCORING, system="s", messages=[], max_tokens=10
    )
    assert sink.entries[0].input_tokens == 12
    assert sink.entries[0].output_tokens == 34
