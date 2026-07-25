"""Router contract + auth tests with an in-memory fake service (no Postgres)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from li_api.auth import require_api_key
from li_api.deps import get_service
from li_api.main import create_app
from li_api.schemas import (
    AccountSummary,
    CostSummary,
    MergeCandidate,
    ReviewRequest,
    ReviewResult,
)

COMPANY = uuid.UUID("11111111-1111-1111-1111-111111111111")
CUSTOMER = uuid.UUID("22222222-2222-2222-2222-222222222222")


class FakeService:
    def __init__(self) -> None:
        self.reviews: list[ReviewRequest] = []

    def review_queue(self) -> list[AccountSummary]:
        return [
            AccountSummary(
                score_id=uuid.uuid4(),
                company_id=COMPANY,
                customer_id=CUSTOMER,
                company_name="Fictional Widgets Pvt Ltd",
                value=Decimal("80.00"),
                band="warm",
                rubric_version="r1",
                model_version="claude-sonnet-5",
            )
        ]

    def record_review(self, request: ReviewRequest) -> ReviewResult:
        self.reviews.append(request)
        return ReviewResult(id=uuid.uuid4(), decision=request.decision)

    def merge_queue(self) -> list[MergeCandidate]:
        return [
            MergeCandidate(
                id=uuid.uuid4(),
                source="registry_gst",
                raw_name="Ambiguous Traders",
                candidate_company_id=None,
                status="pending",
            )
        ]

    def cost_summary(self) -> CostSummary:
        return CostSummary(
            total_inr=Decimal("249.00"),
            by_stage={"pass1_triggers": Decimal("83.00"), "pass2_research": Decimal("166.00")},
        )


@pytest.fixture
def fake() -> FakeService:
    return FakeService()


@pytest.fixture
def client(fake: FakeService) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_service] = lambda: fake
    # Auth is overridden to a no-op EXCEPT in the auth-specific tests below.
    app.dependency_overrides[require_api_key] = lambda: None
    return TestClient(app)


def test_health_needs_no_auth() -> None:
    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok"}


def test_review_queue_returns_scored_accounts(client: TestClient) -> None:
    response = client.get("/qa/queue")
    assert response.status_code == 200
    body = response.json()
    assert body[0]["company_name"] == "Fictional Widgets Pvt Ltd"
    assert body[0]["band"] == "warm"


def test_record_review_writes_through(client: TestClient, fake: FakeService) -> None:
    payload = {
        "company_id": str(COMPANY),
        "customer_id": str(CUSTOMER),
        "reviewer": "alice",
        "decision": "approve",
        "notes": "solid triggers",
    }
    response = client.post("/qa/review", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "approve"
    assert fake.reviews[0].reviewer == "alice"


def test_invalid_decision_is_rejected(client: TestClient) -> None:
    payload = {
        "company_id": str(COMPANY),
        "customer_id": str(CUSTOMER),
        "reviewer": "alice",
        "decision": "maybe",  # not a ReviewDecision
    }
    assert client.post("/qa/review", json=payload).status_code == 422


def test_merge_queue_and_costs(client: TestClient) -> None:
    assert client.get("/qa/merge-queue").json()[0]["source"] == "registry_gst"
    costs = client.get("/costs").json()
    assert costs["total_inr"] == "249.00"
    assert "pass1_triggers" in costs["by_stage"]


# ---- auth (no override) ----


def test_data_routes_require_api_key(fake: FakeService, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERNAL_API_KEY", "secret-key")
    from li_core.config import get_settings

    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_service] = lambda: fake
    client = TestClient(app)

    assert client.get("/qa/queue").status_code == 401
    assert client.get("/qa/queue", headers={"x-api-key": "wrong"}).status_code == 401
    assert client.get("/qa/queue", headers={"x-api-key": "secret-key"}).status_code == 200
    get_settings.cache_clear()
