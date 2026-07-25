"""Cost board: ₹ rollups from the cost ledger (docs/ARCHITECTURE.md §10)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from li_api.deps import get_service
from li_api.schemas import CostSummary
from li_api.service import QaService

router = APIRouter(prefix="/costs", tags=["costs"])


@router.get("", response_model=CostSummary)
def cost_summary(service: QaService = Depends(get_service)) -> CostSummary:
    return service.cost_summary()
