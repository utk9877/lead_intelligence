from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class SignalType(StrEnum):
    """The six buying-trigger types — mirrors PROJECT_SPEC.md §4 exactly."""

    FUNDING_ROUND = "funding_round"
    HIRING_SURGE = "hiring_surge"
    NEW_INCORPORATION = "new_incorporation"
    GST_REGISTRATION = "gst_registration"
    EXPANSION = "expansion"
    TECH_ADOPTION = "tech_adoption"


@dataclass(frozen=True, slots=True)
class Signal:
    """An observed buying trigger, always backed by evidence."""

    company_id: UUID
    type: SignalType
    observed_at: datetime
    evidence_id: UUID
    payload: Mapping[str, object] = field(default_factory=dict)
