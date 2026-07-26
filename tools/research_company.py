"""Research ONE real company from a JSON brief and print a deliverable account card.

This is the operator engine for the semi-manual service: you gather 2-4 real,
public, company-level signals about a target company (funding news, hiring, tech,
incorporation), drop them in a JSON file with their source URLs, and this runs the
three-pass pipeline (triggers → deep-fit research → scoring) against your chosen
open-source model and prints an evidence-cited "why this account, why now" you can
send to a prospect.

Company-level facts only (ADR-005) — never put a person's name/email/phone in the
signals. Every claim in the output is tied to a source URL you provided.

Usage:
    export OPENAI_BASE_URL="https://api.groq.com/openai/v1"
    export OPENAI_API_KEY="gsk_..."
    export DRY_RUN_MODEL="llama-3.3-70b-versatile"
    uv run python tools/research_company.py path/to/brief.json

See docs/gtm/example-target.json for the brief format.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

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


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"set {name} (see the module docstring)")
    return value


def _evidence_for(source_url: str, text: str) -> Evidence:
    # In manual mode there is no stored snapshot; the citation IS the source URL.
    return Evidence(
        id=uuid.uuid4(),
        source_url=source_url,
        content_hash=hashlib.sha256(text.encode()).hexdigest(),
        snapshot_key=source_url,
        captured_at=datetime.now(UTC),
    )


def main() -> None:  # pragma: no cover - operator script
    if len(sys.argv) < 2:
        raise SystemExit("usage: uv run python tools/research_company.py <brief.json>")
    brief = json.loads(Path(sys.argv[1]).read_text())

    base_url = _require("OPENAI_BASE_URL")
    api_key = _require("OPENAI_API_KEY")
    model = _require("DRY_RUN_MODEL")
    register_model_pricing(
        model,
        Decimal(os.environ.get("DRY_RUN_INPUT_USD", "0.59")),
        Decimal(os.environ.get("DRY_RUN_OUTPUT_USD", "0.79")),
    )

    company_id = uuid.uuid4()
    customer_id = uuid.uuid4()

    observations = []
    evidence = []
    for obs in brief["observations"]:
        ev = _evidence_for(obs["source_url"], obs["text"])
        evidence.append(ev)
        observations.append(Observation(text=obs["text"], evidence_id=ev.id))
    evidence_set = EvidenceSet(evidence)

    company = brief["company"]
    facts = CompanyFacts(
        company_id=company_id,
        name=company["name"],
        cin=company.get("cin"),
        gstin=company.get("gstin"),
        domain=company.get("domain"),
        observations=observations,
    )
    customer = brief["customer"]
    icp = CustomerICP(
        customer_id=customer_id, offering=customer["offering"], niche=customer["niche"]
    )
    tools = ToolContext(
        graph_lookup=lambda _i: json.dumps({"name": company["name"]}),
        site_fetch=lambda _i: "",
        registry_fetch=lambda _i: json.dumps({"status": "active"}),
        snapshot_read=lambda _i: "",
    )

    client = OpenAICompatibleClient(base_url=base_url, api_key=api_key, model=model)
    sink = InMemoryCostSink()
    metered = MeteredClient(client, sink, company_id=company_id, customer_id=customer_id)

    print(f"→ researching {company['name']} with {model} …\n")
    result = run_pipeline(metered, facts, evidence_set, tools, icp)

    if result.account is None:
        print("No buying trigger detected in the signals you provided.")
        print("Add stronger public signals (a recent funding round, a hiring surge) and retry.")
        return

    assert result.score is not None
    card = render_account_card(result.account, evidence_set)
    print("=" * 64)
    print(f"ACCOUNT: {company['name']}")
    print(f"BAND: {result.score.band.value.upper()}   SCORE: {result.score.value}/100")
    print("=" * 64)
    print(f"\nWHY NOW\n{result.account.why_now}\n")
    print(f"WHY FIT (for: {customer['offering']})\n{result.account.why_fit}\n")
    print("EVIDENCE-CITED CLAIMS")
    for claim in card["claims"]:
        print(f"  • {claim['text']}\n      source: {claim['source_url']}")
    print(f"\nSCORING RATIONALE\n{result.score.rationale}")
    print(f"\n(model cost for this account: ₹{sink.total_inr():.4f} — illustrative)")


if __name__ == "__main__":  # pragma: no cover
    main()
