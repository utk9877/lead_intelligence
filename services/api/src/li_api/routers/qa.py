"""QA gate endpoints: the review queue, recording a review, and the merge queue."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from li_api.deps import get_service
from li_api.schemas import AccountSummary, MergeCandidate, ReviewRequest, ReviewResult
from li_api.service import QaService

router = APIRouter(prefix="/qa", tags=["qa"])


@router.get("/queue", response_model=list[AccountSummary])
def review_queue(service: QaService = Depends(get_service)) -> list[AccountSummary]:
    return service.review_queue()


@router.post("/review", response_model=ReviewResult)
def record_review(
    request: ReviewRequest, service: QaService = Depends(get_service)
) -> ReviewResult:
    return service.record_review(request)


@router.get("/merge-queue", response_model=list[MergeCandidate])
def merge_queue(service: QaService = Depends(get_service)) -> list[MergeCandidate]:
    return service.merge_queue()
