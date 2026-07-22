"""Job-board adapter — POSTING-LEVEL ONLY (ADR-005).

Aggregates a company's public postings on a third-party board into a hiring
signal (count + role titles). Never person records. Same posting-level contract
as the careers-page adapter.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from li_core.models import SignalType

from li_ingestion.adapters.base import Adapter, AdapterResult
from li_ingestion.artifacts import CandidateCompany, RawArtifact
from li_ingestion.normalize import build_signal, posting_summary


class JobBoardsAdapter(Adapter):
    name = "job_boards"

    def parse(self, artifact: RawArtifact) -> AdapterResult:
        data = json.loads(artifact.body)
        company = CandidateCompany(name=data["company_name"])
        roles = [posting["title"] for posting in data.get("postings", [])]
        observed = datetime.fromisoformat(data["captured_at"]).replace(tzinfo=UTC)
        signal = build_signal(
            signal_type=SignalType.HIRING_SURGE,
            observed_at=observed,
            payload=posting_summary(roles, open_count=len(roles)),
            context=self.name,
        )
        return AdapterResult(companies=[company], signals=[signal])
