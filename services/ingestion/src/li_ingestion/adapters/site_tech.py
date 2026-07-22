"""Company-site tech-detection adapter — emits TECH_ADOPTION signals.

Detects a company's technology stack from its own site markup (script/meta
fingerprints). Company-level by nature; no person data involved.
"""

from __future__ import annotations

import re
from datetime import UTC

from li_core.models import SignalType

from li_ingestion.adapters.base import Adapter, AdapterResult
from li_ingestion.artifacts import CandidateCompany, RawArtifact
from li_ingestion.normalize import build_signal

# Minimal fingerprint table; extended per niche as detection needs grow (§12-T2).
# Anchored to asset hosts / markup fingerprints, never bare words — otherwise page
# prose mentioning a vendor would false-positive a TECH_ADOPTION signal.
_FINGERPRINTS: dict[str, re.Pattern[bytes]] = {
    "shopify": re.compile(rb"cdn\.shopify\.com|Shopify\.theme"),
    "woocommerce": re.compile(rb"/plugins/woocommerce/|woocommerce-[a-z]+\.(?:css|js)|wc-ajax"),
    "razorpay": re.compile(rb"checkout\.razorpay\.com"),
    "hubspot": re.compile(rb"js\.hs-scripts\.com"),
    "segment": re.compile(rb"cdn\.segment\.com"),
}


class SiteTechAdapter(Adapter):
    name = "site_tech"

    def __init__(self, domain: str) -> None:
        self._domain = domain

    def parse(self, artifact: RawArtifact) -> AdapterResult:
        detected = sorted(
            name for name, pattern in _FINGERPRINTS.items() if pattern.search(artifact.body)
        )
        company = CandidateCompany(name=self._domain, domain=self._domain)
        signals = []
        if detected:
            signals.append(
                build_signal(
                    signal_type=SignalType.TECH_ADOPTION,
                    observed_at=artifact.fetched_at.astimezone(UTC),
                    payload={"technologies": detected, "domain": self._domain},
                    context=self.name,
                )
            )
        return AdapterResult(companies=[company], signals=signals)
