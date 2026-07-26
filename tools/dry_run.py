"""Real-model dry run of the three-pass pipeline on ONE fictional company.

Runs pass 1 (triggers) → pass 2 (deep-fit research, with tools) → pass 3 (scoring)
against an OpenAI-compatible open-source model endpoint, then prints the researched,
evidence-cited account, the score, and the cost ledger. No database needed.

Set these env vars (example values are for Groq; any OpenAI-compatible endpoint
works — OpenRouter, Together, Fireworks, DeepSeek, a local Ollama/vLLM):

    export OPENAI_BASE_URL="https://api.groq.com/openai/v1"
    export OPENAI_API_KEY="gsk_..."
    export DRY_RUN_MODEL="llama-3.3-70b-versatile"
    # optional list price per 1M tokens (defaults below), for the cost ledger:
    export DRY_RUN_INPUT_USD="0.59"
    export DRY_RUN_OUTPUT_USD="0.79"

Then:  uv run python tools/dry_run.py

The model must return valid JSON for each pass — use a capable instruct model
(llama-3.3-70b, qwen2.5-72b, deepseek-chat, etc.), not a tiny one.
"""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from li_agents.evidence import EvidenceSet, render_account_card
from li_agents.models import CompanyFacts, CustomerICP, Observation
from li_agents.pass2_research import ToolContext
from li_agents.pipeline import run_pipeline
from li_core.models import Evidence
from li_llm import (
    InMemoryCostSink,
    MeteredClient,
    OpenAICompatibleClient,
    register_model_pricing,
)

NOW = datetime.now(UTC)
EV_FUNDING = uuid.uuid4()
EV_HIRING = uuid.uuid4()
COMPANY = uuid.uuid4()
CUSTOMER = uuid.uuid4()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"set {name} (see the module docstring for the full list)")
    return value


def main() -> None:  # pragma: no cover - operator script
    base_url = _require("OPENAI_BASE_URL")
    api_key = _require("OPENAI_API_KEY")
    model = _require("DRY_RUN_MODEL")
    register_model_pricing(
        model,
        Decimal(os.environ.get("DRY_RUN_INPUT_USD", "0.59")),
        Decimal(os.environ.get("DRY_RUN_OUTPUT_USD", "0.79")),
    )

    client = OpenAICompatibleClient(base_url=base_url, api_key=api_key, model=model)
    sink = InMemoryCostSink()
    metered = MeteredClient(client, sink, company_id=COMPANY, customer_id=CUSTOMER)

    evidence_set = EvidenceSet(
        [
            Evidence(
                id=EV_FUNDING,
                source_url="https://feeds.example-news.test/1",
                content_hash="1" * 64,
                snapshot_key="k1",
                captured_at=NOW,
            ),
            Evidence(
                id=EV_HIRING,
                source_url="https://careers.example-co.test/jobs",
                content_hash="2" * 64,
                snapshot_key="k2",
                captured_at=NOW,
            ),
        ]
    )
    facts = CompanyFacts(
        company_id=COMPANY,
        name="Fictional Widgets Pvt Ltd",
        cin="U12345MH2019PTC123456",
        domain="fictional-widgets.test",
        observations=[
            Observation("Raised a ₹40Cr Series A in May 2026", EV_FUNDING),
            Observation("Posted 6 DevOps/SRE roles in the last two months", EV_HIRING),
        ],
    )
    icp = CustomerICP(
        customer_id=CUSTOMER,
        offering="a DevOps automation SaaS (CI/CD, observability)",
        niche="funded Indian SMBs scaling their infrastructure",
    )
    tools = ToolContext(
        graph_lookup=lambda _i: '{"signals": ["funding_round", "hiring_surge"]}',
        site_fetch=lambda _i: "<html>We are hiring DevOps engineers.</html>",
        registry_fetch=lambda _i: '{"status": "active", "incorporation_year": 2019}',
        snapshot_read=lambda _i: "evidence snapshot content",
    )

    print(f"→ running the 3-pass pipeline with {model} …\n")
    result = run_pipeline(metered, facts, evidence_set, tools, icp)

    print(f"TRIGGERS: {[t.type.value for t in result.triggers]}\n")
    if result.account is None:
        print("No buying trigger fired — gated out before research. (Try a stronger model.)")
    else:
        print(f"WHY NOW: {result.account.why_now}")
        print(f"WHY FIT: {result.account.why_fit}")
        print("CLAIMS (each must cite evidence):")
        card = render_account_card(result.account, evidence_set)
        for claim in card["claims"]:
            print(f"  • {claim['text']}\n      source: {claim['source_url']}")
        assert result.score is not None
        print(
            f"\nSCORE: {result.score.value} ({result.score.band.value}) — {result.score.rationale}"
        )

    print("\nCOST LEDGER (illustrative):")
    for entry in sink.entries:
        print(
            f"  {entry.stage.value:<16} {entry.model:<24} ₹{entry.cost_inr:.4f}  "
            f"({entry.input_tokens} in / {entry.output_tokens} out)"
        )
    print(f"  {'TOTAL':<16} {'':<24} ₹{sink.total_inr():.4f}")


if __name__ == "__main__":  # pragma: no cover
    main()
