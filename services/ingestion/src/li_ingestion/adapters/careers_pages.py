"""Careers-page adapter — POSTING-LEVEL ONLY (ADR-005).

Reads a company's own careers page and extracts only posting titles and an open
count. It never reads or stores applicant or recruiter person data; the output
type has no name/email fields, and the hiring signal is an aggregate. The real
fetch uses Playwright (JS-heavy pages); parsing here is transport-agnostic.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from li_core.models import SignalType

from li_ingestion.adapters.base import Adapter, AdapterResult
from li_ingestion.artifacts import CandidateCompany, RawArtifact
from li_ingestion.normalize import build_signal, posting_summary


class CareersPagesAdapter(Adapter):
    name = "careers_pages"

    def parse(self, artifact: RawArtifact) -> AdapterResult:
        page = json.loads(artifact.body)
        company = CandidateCompany(name=page["company_name"], domain=page.get("company_domain"))
        # Only titles are read from each posting — nothing person-level.
        roles = [posting["title"] for posting in page.get("postings", [])]
        observed = datetime.fromisoformat(page["captured_at"]).replace(tzinfo=UTC)
        signal = build_signal(
            signal_type=SignalType.HIRING_SURGE,
            observed_at=observed,
            payload=posting_summary(roles, open_count=len(roles)),
            context=self.name,
        )
        return AdapterResult(companies=[company], signals=[signal])
