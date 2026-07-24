"""Pass 1 — trigger classification (SMALL tier, batched, cheap).

Screens a company's observations into the six buying-trigger types. Runs on many
companies so only the triggered ones reach the expensive research pass.
"""

from __future__ import annotations

import json
import uuid

from li_core.models import SignalType
from li_llm.ledger import CostStage
from li_llm.metered import MeteredClient

from li_agents.models import CompanyFacts, TriggerFinding
from li_agents.parsing import ModelOutputError, parse_json_object
from li_agents.prompts import PASS1_SYSTEM


def classify_triggers(metered: MeteredClient, facts: CompanyFacts) -> list[TriggerFinding]:
    if not facts.observations:
        return []
    allowed_ids = {o.evidence_id for o in facts.observations}
    allowed_types = ", ".join(s.value for s in SignalType)  # source of truth, no drift
    lines = [{"observation": o.text, "evidence_id": str(o.evidence_id)} for o in facts.observations]
    user = (
        f"Company: {facts.name}\nObservations:\n{json.dumps(lines, indent=2)}\n\n"
        f"Allowed trigger types: {allowed_types}.\n"
        'Respond with JSON: {"triggers": [{"type": <trigger>, "confidence": <0-1>, '
        '"evidence_id": <id>}]}. Only include observations that clearly support a trigger.'
    )
    response = metered.run(
        stage=CostStage.PASS1_TRIGGERS,
        system=PASS1_SYSTEM,
        messages=[{"role": "user", "content": user}],
        max_tokens=1024,
    )
    data = parse_json_object(response.text)
    findings: list[TriggerFinding] = []
    for raw in data.get("triggers", []):
        try:
            signal = SignalType(raw["type"])
            evidence_id = uuid.UUID(str(raw["evidence_id"]))
            confidence = float(raw["confidence"])
        except (KeyError, ValueError, TypeError) as error:
            raise ModelOutputError(f"malformed trigger: {raw!r}") from error
        if not 0.0 <= confidence <= 1.0:
            raise ModelOutputError(f"trigger confidence out of range: {confidence}")
        # A trigger may only cite evidence that was actually provided to the pass.
        if evidence_id not in allowed_ids:
            raise ModelOutputError(f"trigger cites unknown evidence_id {evidence_id}")
        findings.append(TriggerFinding(type=signal, confidence=confidence, evidence_id=evidence_id))
    return findings
