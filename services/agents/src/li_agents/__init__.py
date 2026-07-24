"""Three-pass pipeline: trigger detection, deep-fit research, warm scoring."""

from li_agents.evidence import EvidenceSet, UncitedClaimError, render_account_card
from li_agents.models import (
    AccountScore,
    Claim,
    CompanyFacts,
    CustomerICP,
    Observation,
    ResearchedAccount,
    TriggerFinding,
)
from li_agents.pipeline import PipelineResult, run_pipeline

__version__ = "0.1.0"

__all__ = [
    "AccountScore",
    "Claim",
    "CompanyFacts",
    "CustomerICP",
    "EvidenceSet",
    "Observation",
    "PipelineResult",
    "ResearchedAccount",
    "TriggerFinding",
    "UncitedClaimError",
    "render_account_card",
    "run_pipeline",
]
