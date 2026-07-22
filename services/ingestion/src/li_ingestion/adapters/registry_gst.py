"""GSTIN verification/monitoring adapter (ADR-004).

Vendor-neutral JSON shape until a vendor is chosen (QUESTIONS.md#api-vendor).
Anchors on GSTIN with checksum validation; emits a GST_REGISTRATION signal for a
newly active registration.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from li_core.ids import parse_gstin
from li_core.models import SignalType

from li_ingestion.adapters.base import Adapter, AdapterResult
from li_ingestion.artifacts import CandidateCompany, CandidateSignal, RawArtifact
from li_ingestion.normalize import build_signal


class RegistryGstAdapter(Adapter):
    name = "registry_gst"

    def parse(self, artifact: RawArtifact) -> AdapterResult:
        record = json.loads(artifact.body)
        gstin = parse_gstin(record["gstin"]).normalized
        company = CandidateCompany(name=record["legal_name"], gstin=gstin)
        signals: list[CandidateSignal] = []
        registered = record.get("registration_date")
        if registered is not None and record.get("status", "").lower() == "active":
            signals.append(
                build_signal(
                    signal_type=SignalType.GST_REGISTRATION,
                    observed_at=datetime.fromisoformat(registered).replace(tzinfo=UTC),
                    payload={"gstin": gstin, "registration_date": registered},
                    context=self.name,
                )
            )
        return AdapterResult(companies=[company], signals=signals)
