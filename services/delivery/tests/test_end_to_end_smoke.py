"""End-to-end smoke: fictional company → resolve → agents (stub LLM) → QA approve
→ delivery card → feedback, through the real database (docs/ARCHITECTURE.md §8).

This is the tooling the design-partner concept proof runs on (ROADMAP.md
#design-partner): the whole loop, on one seed company, with every claim cited and
the cost ledger populated — proven in CI on Postgres. All data is fictional.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from li_agents.evidence import EvidenceSet
from li_agents.models import CompanyFacts, CustomerICP, Observation
from li_agents.pass2_research import ToolContext
from li_agents.pipeline import run_pipeline
from li_core.models import CandidateCompany, Evidence
from li_db.orm import Customer, Score
from li_db.orm import Evidence as OrmEvidence
from li_db.repositories import (
    CompanyRepository,
    DeliveryRepository,
    FeedbackAlreadyRecordedError,
    QaRepository,
    ResolutionRepository,
)
from li_db.testing import database_url
from li_delivery.cards import render_delivery_card
from li_llm.ledger import InMemoryCostSink
from li_llm.metered import MeteredClient
from li_llm.stub import StubLLMClient
from li_llm.types import LLMResponse, Usage
from li_resolver.outcomes import Disposition
from li_resolver.resolve import resolve
from sqlalchemy.orm import Session

pytestmark = pytest.mark.skipif(
    database_url() is None, reason="DATABASE_URL not set (Postgres integration tests)"
)

NOW = datetime(2026, 7, 26, tzinfo=UTC)
CIN = "U12345MH2019PTC123456"
GSTIN = "27ZZZZZ9999Z1Z8"
EV_FUNDING = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
EV_HIRING = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000002")


def _text(payload: dict[str, object]) -> LLMResponse:
    return LLMResponse(
        model="stub-model",
        stop_reason="end_turn",
        text=json.dumps(payload),
        tool_calls=[],
        usage=Usage(input_tokens=300, output_tokens=120),
        raw_content=[],
    )


def test_end_to_end_smoke(db_session: Session) -> None:
    # 1. Evidence (snapshotted upstream): persist the ORM rows, and build the
    # account's EvidenceSet from the equivalent domain objects the pipeline uses.
    rows = [
        ("1" * 64, "k1", "https://feeds.example-news.test/1", EV_FUNDING),
        ("2" * 64, "k2", "https://careers.example-co.test/jobs", EV_HIRING),
    ]
    db_session.add_all(
        OrmEvidence(id=eid, source_url=url, content_hash=h, snapshot_key=key, captured_at=NOW)
        for h, key, url, eid in rows
    )
    db_session.flush()
    evidence_set = EvidenceSet(
        Evidence(id=eid, source_url=url, content_hash=h, snapshot_key=key, captured_at=NOW)
        for h, key, url, eid in rows
    )

    # 2. Resolve a fictional company onto its CIN/GSTIN (creates it).
    resolution = resolve(
        CandidateCompany(name="Fictional Widgets Pvt Ltd", cin=CIN, gstin=GSTIN),
        CompanyRepository(db_session),
        ResolutionRepository(db_session),
        source="smoke",
    )
    assert resolution.disposition is Disposition.CREATED
    company_id = resolution.company_id
    assert company_id is not None

    customer = Customer(name="DevOps SaaS Co", niche="funded SMBs")
    db_session.add(customer)
    db_session.flush()

    # 3. Agents pipeline against a stub LLM (triggers → research → score).
    facts = CompanyFacts(
        company_id=company_id,
        name="Fictional Widgets Pvt Ltd",
        cin=CIN,
        observations=[
            Observation("Raised a Series A in May 2026", EV_FUNDING),
            Observation("Posted 6 DevOps/SRE roles since", EV_HIRING),
        ],
    )
    icp = CustomerICP(customer.id, offering="DevOps SaaS", niche="funded SMBs")
    tools = ToolContext(
        graph_lookup=lambda _i: "{}",
        site_fetch=lambda _i: "<html></html>",
        registry_fetch=lambda _i: "{}",
        snapshot_read=lambda _i: "bytes",
    )
    stub = StubLLMClient(
        [
            _text(
                {
                    "triggers": [
                        {"type": "funding_round", "confidence": 0.9, "evidence_id": str(EV_FUNDING)}
                    ]
                }
            ),
            _text(
                {
                    "why_now": "Raised Series A and scaling infra",
                    "why_fit": "Needs DevOps tooling",
                    "claims": [
                        {"text": "Series A in May 2026", "evidence_id": str(EV_FUNDING)},
                        {"text": "6 SRE roles open", "evidence_id": str(EV_HIRING)},
                    ],
                }
            ),
            _text({"value": 82, "band": "warm", "rationale": "strong triggers, good fit"}),
        ]
    )
    sink = InMemoryCostSink()
    metered = MeteredClient(stub, sink, company_id=company_id, customer_id=customer.id)
    result = run_pipeline(metered, facts, evidence_set, tools, icp)
    assert result.account is not None and result.score is not None
    assert len(sink.entries) == 3  # cost ledger populated for all three passes

    # 4. Persist the score, then the human QA gate approves it.
    score = Score(
        company_id=company_id,
        customer_id=customer.id,
        value=Decimal(str(result.score.value)),
        band=result.score.band,
        rubric_version=result.score.rubric_version,
        model_version=result.score.model_version,
    )
    db_session.add(score)
    db_session.flush()

    qa = QaRepository(db_session)
    assert score.id in [a.score_id for a in qa.review_queue()]
    review = qa.record_review(
        score_id=score.id,
        company_id=company_id,
        customer_id=customer.id,
        reviewer="alice",
        decision="approve",
    )

    # 5. Render the delivered card (every claim cited) and record the delivery.
    card = render_delivery_card(result.account, result.score, evidence_set)
    assert card["band"] == "warm"
    assert len(card["claims"]) == 2
    assert all(c["snapshot_key"] for c in card["claims"])  # citations resolve

    deliveries = DeliveryRepository(db_session)
    delivery = deliveries.record_delivery(
        customer_id=customer.id, company_id=company_id, score_id=score.id, qa_review_id=review.id
    )

    # 6. Customer feedback — the labelled data closing the loop.
    deliveries.record_feedback(delivery.id, "pursue")
    labelled = deliveries.with_feedback()
    assert len(labelled) == 1
    assert labelled[0].feedback is not None and labelled[0].feedback.value == "pursue"

    # Feedback is set-once: a second verdict must not silently overwrite the label.
    with pytest.raises(FeedbackAlreadyRecordedError):
        deliveries.record_feedback(delivery.id, "reject")
