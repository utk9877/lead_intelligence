"""Pass 3 — warm scoring against a fixed rubric (MID tier).

"Warm" and "hot" are bands on one 0-100 score; the threshold is tuned over time by
customer feedback. The rubric version is recorded so a scoring change is traceable
in the precision metric (PROJECT_SPEC.md §6).
"""

from __future__ import annotations

import json

from li_core.models import ScoreBand
from li_llm.ledger import CostStage
from li_llm.metered import MeteredClient

from li_agents.models import AccountScore, ResearchedAccount
from li_agents.parsing import ModelOutputError, parse_json_object
from li_agents.prompts import PASS3_SYSTEM, RUBRIC_VERSION


def score_account(metered: MeteredClient, account: ResearchedAccount) -> AccountScore:
    payload = {
        "why_now": account.why_now,
        "why_fit": account.why_fit,
        "claims": [c.text for c in account.claims],
    }
    user = f"Score this researched account:\n{json.dumps(payload, indent=2)}"
    response = metered.run(
        stage=CostStage.PASS3_SCORING,
        system=PASS3_SYSTEM,
        messages=[{"role": "user", "content": user}],
        max_tokens=1024,
    )
    data = parse_json_object(response.text)
    try:
        value = float(data["value"])
        band = ScoreBand(data["band"])
        rationale = str(data["rationale"])
    except (KeyError, ValueError, TypeError) as error:
        raise ModelOutputError(f"malformed score: {response.text[:200]!r}") from error
    if not 0.0 <= value <= 100.0:
        raise ModelOutputError(f"score value out of range: {value}")
    return AccountScore(
        value=value,
        band=band,
        rubric_version=RUBRIC_VERSION,
        model_version=response.model,
        rationale=rationale,
    )
