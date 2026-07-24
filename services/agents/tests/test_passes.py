import uuid

import pytest
from agents_fixtures import (
    EV_FUNDING,
    EV_HIRING,
    research_json,
    score_json,
    tool_use_response,
    triggers_json,
)
from li_agents.evidence import EvidenceSet, UncitedClaimError
from li_agents.models import CompanyFacts, ResearchedAccount
from li_agents.parsing import ModelOutputError
from li_agents.pass1_triggers import classify_triggers
from li_agents.pass2_research import ResearchIncompleteError, ToolContext, research_account
from li_agents.pass3_scoring import score_account
from li_core.models import ScoreBand, SignalType
from li_llm.ledger import InMemoryCostSink
from li_llm.metered import MeteredClient
from li_llm.stub import StubLLMClient
from li_llm.types import LLMResponse, Usage


def _metered(*responses: object) -> MeteredClient:
    stub = StubLLMClient(list(responses))  # type: ignore[arg-type]
    return MeteredClient(stub, InMemoryCostSink())


# ---- pass 1 ----


def test_pass1_classifies_and_validates_evidence(facts: CompanyFacts) -> None:
    metered = _metered(
        triggers_json(
            ("funding_round", 0.9, EV_FUNDING),
            ("hiring_surge", 0.8, EV_HIRING),
        )
    )
    findings = classify_triggers(metered, facts)
    assert {f.type for f in findings} == {SignalType.FUNDING_ROUND, SignalType.HIRING_SURGE}


def test_pass1_rejects_trigger_citing_unknown_evidence(facts: CompanyFacts) -> None:
    metered = _metered(triggers_json(("funding_round", 0.9, uuid.uuid4())))
    with pytest.raises(ModelOutputError, match="unknown evidence_id"):
        classify_triggers(metered, facts)


def test_pass1_no_observations_short_circuits() -> None:
    facts = CompanyFacts(company_id=uuid.uuid4(), name="Empty Co", observations=[])
    # No LLM call should be made when there is nothing to classify.
    metered = _metered()  # empty queue → any call would raise
    assert classify_triggers(metered, facts) == []


# ---- pass 2 ----


def test_pass2_runs_tool_loop_then_returns_cited_account(
    facts: CompanyFacts, evidence_set: EvidenceSet, tools: ToolContext
) -> None:
    metered = _metered(
        tool_use_response("graph_lookup", {"company_id": str(facts.company_id)}),
        research_json(
            "Raised Series A and hiring DevOps",
            "Fits a DevOps SaaS seller",
            [("Series A in May 2026", EV_FUNDING), ("6 SRE roles open", EV_HIRING)],
        ),
    )
    account = research_account(metered, facts, evidence_set, tools, system_preamble="preamble")
    assert isinstance(account, ResearchedAccount)
    assert len(account.claims) == 2
    assert account.why_now


def test_pass2_rejects_account_with_uncited_claim(
    facts: CompanyFacts, evidence_set: EvidenceSet, tools: ToolContext
) -> None:
    metered = _metered(
        research_json("now", "fit", [("fabricated claim", uuid.uuid4())])  # unknown evidence
    )
    with pytest.raises(UncitedClaimError):
        research_account(metered, facts, evidence_set, tools, system_preamble="p")


def test_pass2_tool_loop_is_bounded(
    facts: CompanyFacts, evidence_set: EvidenceSet, tools: ToolContext
) -> None:
    # A model that only ever calls tools must not loop forever.
    def always_tool(_request: object) -> object:
        return tool_use_response("graph_lookup", {"company_id": "x"})

    stub = StubLLMClient(responder=always_tool)  # type: ignore[arg-type]
    metered = MeteredClient(stub, InMemoryCostSink())
    with pytest.raises(ResearchIncompleteError):
        research_account(metered, facts, evidence_set, tools, system_preamble="p")


def test_pass2_unknown_tool_call_is_rejected(
    facts: CompanyFacts, evidence_set: EvidenceSet, tools: ToolContext
) -> None:
    metered = _metered(tool_use_response("delete_everything", {}))
    with pytest.raises(ModelOutputError, match="unknown tool"):
        research_account(metered, facts, evidence_set, tools, system_preamble="p")


def test_pass2_refusal_reports_the_stop_reason_not_a_json_error(
    facts: CompanyFacts, evidence_set: EvidenceSet, tools: ToolContext
) -> None:
    # A refusal must not be misreported as "expected JSON, got ''".
    refusal = LLMResponse("m", "refusal", "", [], Usage(input_tokens=1, output_tokens=0))
    metered = _metered(refusal)
    with pytest.raises(ResearchIncompleteError, match="refusal"):
        research_account(metered, facts, evidence_set, tools, system_preamble="p")


def test_pass1_rejects_confidence_out_of_range(facts: CompanyFacts) -> None:
    metered = _metered(triggers_json(("funding_round", 5.0, EV_FUNDING)))
    with pytest.raises(ModelOutputError, match="confidence out of range"):
        classify_triggers(metered, facts)


# ---- pass 3 ----


def test_pass3_scores_and_bands(evidence_set: EvidenceSet) -> None:
    account = ResearchedAccount(company_id=uuid.uuid4(), why_now="n", why_fit="f", claims=())
    metered = _metered(score_json(82.0, "hot", "strong triggers"))
    score = score_account(metered, account)
    assert score.value == 82.0
    assert score.band is ScoreBand.HOT
    assert score.rubric_version


def test_pass3_rejects_out_of_range_value() -> None:
    account = ResearchedAccount(company_id=uuid.uuid4(), why_now="n", why_fit="f", claims=())
    metered = _metered(score_json(150.0, "hot"))
    with pytest.raises(ModelOutputError, match="out of range"):
        score_account(metered, account)
