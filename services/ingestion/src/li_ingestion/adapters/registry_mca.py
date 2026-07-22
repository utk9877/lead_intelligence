"""MCA company-master adapter (ADR-004: pay-per-call registry vendor).

No vendor is chosen yet (QUESTIONS.md#api-vendor), so this parses a vendor-neutral
JSON shape. The real vendor client is a thin transport swap — the compliance gate
and this parser stay the same. It anchors on CIN and validates it, so a bad CIN
from a vendor never becomes a company (ADR-001).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from li_core.ids import parse_cin
from li_core.models import SignalType

from li_ingestion.adapters.base import Adapter, AdapterResult
from li_ingestion.artifacts import CandidateCompany, CandidateSignal, RawArtifact
from li_ingestion.normalize import build_signal


class RegistryMcaAdapter(Adapter):
    name = "registry_mca"

    def parse(self, artifact: RawArtifact) -> AdapterResult:
        record = json.loads(artifact.body)
        cin = parse_cin(record["cin"]).normalized  # validates + canonicalizes
        company = CandidateCompany(
            name=record["name"],
            cin=cin,
            domain=record.get("domain"),
        )
        signals: list[CandidateSignal] = []
        incorporated = record.get("incorporation_date")
        if incorporated is not None:
            signals.append(
                build_signal(
                    signal_type=SignalType.NEW_INCORPORATION,
                    observed_at=datetime.fromisoformat(incorporated).replace(tzinfo=UTC),
                    payload={"cin": cin, "incorporation_date": incorporated},
                    context=self.name,
                )
            )
        return AdapterResult(companies=[company], signals=signals)
