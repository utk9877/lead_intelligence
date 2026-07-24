"""Pass 2 — deep-fit research (FRONTIER tier, direct tool-use loop).

A bounded Claude tool loop: the model calls graph/site/registry/snapshot tools to
gather facts, then returns an evidence-cited case. No heavy agent framework — the
loop is a dozen lines so budget caps and turn limits are explicit and auditable.
Adaptive thinking + high effort are set (never sampling params). Every returned
claim is checked to cite evidence in the account's set before the account is
accepted (evidence.assert_cited).
"""

from __future__ import annotations

import uuid
from typing import Any

from li_core.errors import LeadIntelligenceError
from li_llm.ledger import CostStage
from li_llm.metered import MeteredClient

from li_agents.evidence import EvidenceSet, assert_cited
from li_agents.models import Claim, CompanyFacts, ResearchedAccount
from li_agents.parsing import ModelOutputError, parse_json_object
from li_agents.pass2_research.tools import TOOL_DEFS, ToolContext

_MAX_TURNS = 8


class ResearchIncompleteError(LeadIntelligenceError):
    """The research loop hit its turn limit without producing a final account."""


def research_account(
    metered: MeteredClient,
    facts: CompanyFacts,
    evidence: EvidenceSet,
    tools: ToolContext,
    *,
    system_preamble: str | list[dict[str, Any]],
) -> ResearchedAccount:
    messages: list[dict[str, Any]] = [{"role": "user", "content": _research_prompt(facts)}]
    for _ in range(_MAX_TURNS):
        response = metered.run(
            stage=CostStage.PASS2_RESEARCH,
            system=system_preamble,
            messages=messages,
            tools=TOOL_DEFS,
            thinking=True,
            effort="high",
            max_tokens=8000,
        )
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.raw_content})
            results = [
                {
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": tools.handler(call.name)(call.input),
                }
                for call in response.tool_calls
            ]
            messages.append({"role": "user", "content": results})
            continue
        return _finalize(facts.company_id, response.text, evidence)
    raise ResearchIncompleteError(f"research for {facts.company_id} exceeded {_MAX_TURNS} turns")


def _finalize(company_id: uuid.UUID, text: str, evidence: EvidenceSet) -> ResearchedAccount:
    data = parse_json_object(text)
    try:
        claims = tuple(
            Claim(text=c["text"], evidence_id=uuid.UUID(str(c["evidence_id"])))
            for c in data["claims"]
        )
        account = ResearchedAccount(
            company_id=company_id,
            why_now=str(data["why_now"]),
            why_fit=str(data["why_fit"]),
            claims=claims,
        )
    except (KeyError, ValueError) as error:
        raise ModelOutputError(f"malformed research output: {text[:200]!r}") from error
    # Reject the account if any claim is uncited — before it is ever scored/delivered.
    for claim in account.claims:
        assert_cited(claim, evidence)
    return account


def _research_prompt(facts: CompanyFacts) -> str:
    ids = ", ".join(
        filter(
            None,
            [
                f"CIN {facts.cin}" if facts.cin else "",
                f"GSTIN {facts.gstin}" if facts.gstin else "",
            ],
        )
    )
    return (
        f"Research company {facts.name} (id {facts.company_id}"
        f"{'; ' + ids if ids else ''}). Use the tools to gather evidence, then return "
        "the evidence-cited case as specified. Cite only evidence ids you actually read."
    )
