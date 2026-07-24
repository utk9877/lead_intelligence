"""Three-pass orchestration: triggers → (gate) → deep-fit research → scoring.

Pass 1 gates pass 2: a company with no buying trigger never reaches the expensive
frontier research pass — that gate is the cost control the tiering exists for.
Everything runs through one MeteredClient, so the whole account is budget-capped
and every call is cost-ledgered.
"""

from __future__ import annotations

from dataclasses import dataclass

from li_llm.metered import MeteredClient
from li_llm.prompt_cache import cached_system

from li_agents.evidence import EvidenceSet
from li_agents.models import (
    AccountScore,
    CompanyFacts,
    CustomerICP,
    ResearchedAccount,
    TriggerFinding,
)
from li_agents.pass1_triggers import classify_triggers
from li_agents.pass2_research import ToolContext, research_account
from li_agents.pass3_scoring import score_account
from li_agents.prompts import PASS2_SYSTEM_SUFFIX


@dataclass(frozen=True, slots=True)
class PipelineResult:
    triggers: list[TriggerFinding]
    account: ResearchedAccount | None  # None when no trigger fired (gated out)
    score: AccountScore | None


def run_pipeline(
    metered: MeteredClient,
    facts: CompanyFacts,
    evidence: EvidenceSet,
    tools: ToolContext,
    icp: CustomerICP,
) -> PipelineResult:
    triggers = classify_triggers(metered, facts)
    if not triggers:
        # Gated out — no buying window, no expensive research (docs/ARCHITECTURE.md §2).
        return PipelineResult(triggers=triggers, account=None, score=None)

    # The stable per-customer ICP preamble is the cacheable prefix (prompt caching).
    preamble = cached_system(_icp_preamble(icp) + PASS2_SYSTEM_SUFFIX)
    account = research_account(metered, facts, evidence, tools, system_preamble=preamble)
    score = score_account(metered, account)
    return PipelineResult(triggers=triggers, account=account, score=score)


def _icp_preamble(icp: CustomerICP) -> str:
    return (
        f"The seller's offering: {icp.offering}\n"
        f"They target: {icp.niche}\n"
        "Assess accounts for fit to THIS seller."
    )
