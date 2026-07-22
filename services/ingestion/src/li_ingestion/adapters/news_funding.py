"""News / funding-feed adapter — emits FUNDING_ROUND signals from a feed item.

Vendor-neutral JSON item shape. Company-level only: no journalist/founder person
fields are read; the guard rejects the payload if any slip in.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from li_core.models import SignalType

from li_ingestion.adapters.base import Adapter, AdapterResult
from li_ingestion.artifacts import CandidateCompany, RawArtifact
from li_ingestion.normalize import build_signal


class NewsFundingAdapter(Adapter):
    name = "news_funding"

    def parse(self, artifact: RawArtifact) -> AdapterResult:
        item = json.loads(artifact.body)
        company = CandidateCompany(name=item["company_name"], domain=item.get("company_domain"))
        payload: dict[str, object] = {"company_name": item["company_name"]}
        for key in ("round", "amount_inr_crore", "investors"):
            if key in item:
                payload[key] = item[key]
        signal = build_signal(
            signal_type=SignalType.FUNDING_ROUND,
            observed_at=datetime.fromisoformat(item["published_at"]).replace(tzinfo=UTC),
            payload=payload,
            context=self.name,
        )
        return AdapterResult(companies=[company], signals=[signal])
