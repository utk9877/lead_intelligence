"""Fictional fixtures + stub-response helpers. No real company data, no network."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import pytest
from li_agents.evidence import EvidenceSet
from li_agents.models import CompanyFacts, CustomerICP, Observation
from li_agents.pass2_research.tools import ToolContext
from li_core.models import Evidence
from li_llm.types import LLMResponse, ToolCall, Usage

NOW = datetime(2026, 7, 24, tzinfo=UTC)
COMPANY_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
CUSTOMER_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
EV_FUNDING = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
EV_HIRING = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000002")


def _evidence(evidence_id: uuid.UUID, url: str) -> Evidence:
    return Evidence(
        id=evidence_id,
        source_url=url,
        content_hash="0" * 64,
        snapshot_key=f"snapshots/aa/{evidence_id}",
        captured_at=NOW,
    )


@pytest.fixture
def evidence_set() -> EvidenceSet:
    return EvidenceSet(
        [
            _evidence(EV_FUNDING, "https://feeds.example-news.test/1"),
            _evidence(EV_HIRING, "https://careers.example-co.test/jobs"),
        ]
    )


@pytest.fixture
def facts() -> CompanyFacts:
    return CompanyFacts(
        company_id=COMPANY_ID,
        name="Fictional Widgets Pvt Ltd",
        cin="U12345MH2019PTC123456",
        domain="fictional-widgets.test",
        observations=[
            Observation("Raised a Series A in May 2026", EV_FUNDING),
            Observation("Posted 6 DevOps/SRE roles since", EV_HIRING),
        ],
    )


@pytest.fixture
def icp() -> CustomerICP:
    return CustomerICP(
        customer_id=CUSTOMER_ID,
        offering="DevOps automation SaaS",
        niche="funded Indian SMBs scaling infrastructure",
    )


@pytest.fixture
def tools() -> ToolContext:
    return ToolContext(
        graph_lookup=lambda _i: json.dumps({"signals": ["funding_round", "hiring_surge"]}),
        site_fetch=lambda _i: "<html>careers</html>",
        registry_fetch=lambda _i: json.dumps({"status": "active"}),
        snapshot_read=lambda _i: "snapshot bytes",
    )


# ---- stub-response builders ----


def triggers_json(*items: tuple[str, float, uuid.UUID]) -> LLMResponse:
    payload = {
        "triggers": [{"type": t, "confidence": c, "evidence_id": str(e)} for t, c, e in items]
    }
    return _text(json.dumps(payload))


def research_json(why_now: str, why_fit: str, claims: list[tuple[str, uuid.UUID]]) -> LLMResponse:
    payload = {
        "why_now": why_now,
        "why_fit": why_fit,
        "claims": [{"text": t, "evidence_id": str(e)} for t, e in claims],
    }
    return _text(json.dumps(payload))


def score_json(value: float, band: str, rationale: str = "ok") -> LLMResponse:
    return _text(json.dumps({"value": value, "band": band, "rationale": rationale}))


def tool_use_response(
    name: str, tool_input: dict[str, Any], call_id: str = "toolu_1"
) -> LLMResponse:
    return LLMResponse(
        model="stub-model",
        stop_reason="tool_use",
        text="",
        tool_calls=[ToolCall(id=call_id, name=name, input=tool_input)],
        usage=Usage(input_tokens=200, output_tokens=40),
        raw_content=[{"type": "tool_use", "id": call_id, "name": name, "input": tool_input}],
    )


def _text(text: str) -> LLMResponse:
    return LLMResponse(
        model="stub-model",
        stop_reason="end_turn",
        text=text,
        tool_calls=[],
        usage=Usage(input_tokens=300, output_tokens=120),
        raw_content=[{"type": "text", "text": text}],
    )
