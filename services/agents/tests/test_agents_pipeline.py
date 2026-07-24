from dataclasses import replace
from decimal import Decimal

import pytest
from agents_fixtures import (
    EV_FUNDING,
    EV_HIRING,
    research_json,
    score_json,
    triggers_json,
)
from li_agents.evidence import EvidenceSet
from li_agents.models import CompanyFacts, CustomerICP
from li_agents.pass2_research.tools import ToolContext
from li_agents.pipeline import run_pipeline
from li_llm.budget import BudgetExceededError, BudgetGuard
from li_llm.ledger import CostStage, InMemoryCostSink
from li_llm.metered import MeteredClient
from li_llm.stub import StubLLMClient
from li_llm.types import LLMResponse, Usage


def test_full_pipeline_produces_scored_account(
    facts: CompanyFacts, evidence_set: EvidenceSet, tools: ToolContext, icp: CustomerICP
) -> None:
    sink = InMemoryCostSink()
    stub = StubLLMClient(
        [
            triggers_json(("funding_round", 0.9, EV_FUNDING), ("hiring_surge", 0.8, EV_HIRING)),
            research_json("now", "fit", [("Series A", EV_FUNDING), ("hiring", EV_HIRING)]),
            score_json(80.0, "warm"),
        ]
    )
    metered = MeteredClient(stub, sink, company_id=facts.company_id, customer_id=icp.customer_id)

    result = run_pipeline(metered, facts, evidence_set, tools, icp)

    assert result.account is not None and result.score is not None
    assert result.score.band.value == "warm"
    # One ledger row per pass, in tier order.
    assert [e.stage for e in sink.entries] == [
        CostStage.PASS1_TRIGGERS,
        CostStage.PASS2_RESEARCH,
        CostStage.PASS3_SCORING,
    ]


def test_no_trigger_gates_out_expensive_research(
    facts: CompanyFacts, evidence_set: EvidenceSet, tools: ToolContext, icp: CustomerICP
) -> None:
    sink = InMemoryCostSink()
    # Pass 1 returns no triggers; passes 2 and 3 must never run (queue has only 1 item).
    stub = StubLLMClient([triggers_json()])
    metered = MeteredClient(stub, sink)

    result = run_pipeline(metered, facts, evidence_set, tools, icp)

    assert result.account is None and result.score is None
    assert len(sink.entries) == 1  # only the cheap pass 1 ran
    assert sink.entries[0].stage is CostStage.PASS1_TRIGGERS


def test_budget_cap_aborts_pipeline_at_the_frontier_pass(
    facts: CompanyFacts, evidence_set: EvidenceSet, tools: ToolContext, icp: CustomerICP
) -> None:
    # Pass 1 is cheap; the frontier research pass is billed enough to breach the cap.
    def responder(request: dict[str, object]) -> LLMResponse:
        if request["model"] == "claude-opus-4-8":  # pass 2 — expensive
            base = research_json("now", "fit", [("c", EV_FUNDING)])
            return replace(base, usage=Usage(input_tokens=1_000_000, output_tokens=0))
        return triggers_json(("funding_round", 0.9, EV_FUNDING))

    stub = StubLLMClient(responder=responder)
    sink = InMemoryCostSink()
    # Cap ₹100: pass 1 is tiny, pass 2 at 1M Opus input = ₹415 → breaches.
    metered = MeteredClient(stub, sink, budget=BudgetGuard(Decimal("100")))

    with pytest.raises(BudgetExceededError):
        run_pipeline(metered, facts, evidence_set, tools, icp)
    # The breaching frontier call is on the ledger (pass 1 + pass 2 recorded).
    assert [e.stage for e in sink.entries] == [CostStage.PASS1_TRIGGERS, CostStage.PASS2_RESEARCH]
