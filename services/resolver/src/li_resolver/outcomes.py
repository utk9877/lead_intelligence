"""Resolution outcome types.

`Disposition` is what happened; `ResolutionMethod` is why. `company_id` is set for
MATCHED/CREATED and None for QUEUED items that have no confident company yet.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum


class Disposition(StrEnum):
    MATCHED = "matched"  # resolved to an existing company
    CREATED = "created"  # a new company was created
    QUEUED = "queued"  # ambiguous/conflicting → human merge queue


class ResolutionMethod(StrEnum):
    CIN = "cin"  # hard anchor
    GSTIN = "gstin"  # hard anchor
    CREATED_ANCHORED = "created_anchored"
    IDENTIFIER_CONFLICT = "identifier_conflict"  # cin and gstin point to different companies
    PAN_MATCH = "pan_match"  # same PAN, different GSTIN — probable same entity
    DOMAIN_HINT = "domain_hint"  # unanchored, one domain match
    AMBIGUOUS_DOMAIN = "ambiguous_domain"  # unanchored, several domain matches
    NAME_ONLY = "name_only"  # unanchored, no domain — too weak to auto-resolve


@dataclass(frozen=True, slots=True)
class Resolution:
    disposition: Disposition
    method: ResolutionMethod
    company_id: uuid.UUID | None
    reason: str
