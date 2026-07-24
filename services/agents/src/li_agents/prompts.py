"""Versioned prompt templates.

Prompt changes bump these versions; scores record `model_version` so a change in
scoring behaviour is traceable (docs/ARCHITECTURE.md §4). Kept terse deliberately —
over-prescriptive prompts reduce output quality on current models.
"""

from __future__ import annotations

PASS1_VERSION = "p1-2026-07"
PASS2_VERSION = "p2-2026-07"
RUBRIC_VERSION = "r1-2026-07"

# The allowed trigger vocabulary is SignalType (PROJECT_SPEC.md §4) — classify.py
# derives it from the enum and feeds it to the model, so there is no list to drift.

PASS1_SYSTEM = (
    "You classify company-level observations into buying-trigger types for a B2B "
    "seller. Company-level facts only; never infer or emit person data. Assign each "
    "observation at most one trigger type from the allowed set, with a confidence "
    "0-1, and echo the observation's evidence_id. Respond with JSON only."
)

PASS2_SYSTEM_SUFFIX = (
    "\n\nYou research one company and produce an evidence-cited case for why this "
    "account and why now, tied to the seller's offering. Use the tools to gather "
    "facts; every claim you make MUST cite the evidence_id it came from. Company-"
    "level only. When done, respond with JSON only: "
    '{"why_now": str, "why_fit": str, "claims": [{"text": str, "evidence_id": str}]}.'
)

PASS3_SYSTEM = (
    "You score a researched account against a fixed rubric for one seller: trigger "
    "strength, fit to the offering, recency, and evidence quality. Output JSON only: "
    '{"value": number 0-100, "band": "hot"|"warm"|"not_warm", "rationale": str}.'
)
