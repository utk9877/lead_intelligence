"""Resolver golden set: tricky entity-resolution cases plus measured duplicate and
mismatch rates (QUESTIONS.md#entity-resolution, ASSUMPTIONS.md#entity-resolution).

All identifiers are fictional but structurally valid (GSTIN checksums are computed,
not hand-written). No real company data appears.
"""

from __future__ import annotations

import pytest
from li_core.ids import gstin_check_char
from li_core.models import CandidateCompany
from li_db.orm import Company, ResolutionCandidate
from li_db.repositories import CompanyRepository, ResolutionRepository
from li_db.testing import database_url
from li_resolver.outcomes import Disposition, Resolution, ResolutionMethod
from li_resolver.resolve import resolve
from sqlalchemy import func, select
from sqlalchemy.orm import Session

pytestmark = pytest.mark.skipif(
    database_url() is None, reason="DATABASE_URL not set (Postgres integration tests)"
)


def make_gstin(state: str, pan: str) -> str:
    """Build a checksum-valid GSTIN from a 2-digit state code and a 10-char PAN."""
    first14 = f"{state}{pan}1Z"
    return first14 + gstin_check_char(first14)


CIN_ALPHA = "U12345MH2019PTC100001"
CIN_BETA = "U12345MH2019PTC100002"
PAN_ALPHA = "AAACA1111A"
GST_ALPHA_MH = make_gstin("27", PAN_ALPHA)  # Maharashtra
GST_ALPHA_KA = make_gstin("29", PAN_ALPHA)  # Karnataka, same PAN → same legal entity
GST_BETA = make_gstin("27", "AAACB2222B")


def _resolve(session: Session, candidate: CandidateCompany, source: str = "test") -> Resolution:
    return resolve(
        candidate,
        CompanyRepository(session),
        ResolutionRepository(session),
        source=source,
    )


def _company_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Company)) or 0


def _queue_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(ResolutionCandidate)) or 0


def test_new_cin_creates_then_same_cin_matches_idempotently(db_session: Session) -> None:
    first = _resolve(db_session, CandidateCompany(name="Alpha Pvt Ltd", cin=CIN_ALPHA))
    assert first.disposition is Disposition.CREATED
    second = _resolve(db_session, CandidateCompany(name="Alpha Pvt Ltd", cin=CIN_ALPHA))
    assert second.disposition is Disposition.MATCHED
    assert second.company_id == first.company_id
    assert _company_count(db_session) == 1  # no duplicate


def test_same_name_different_cin_stays_distinct(db_session: Session) -> None:
    a = _resolve(db_session, CandidateCompany(name="Acme", cin=CIN_ALPHA))
    b = _resolve(db_session, CandidateCompany(name="Acme", cin=CIN_BETA))
    assert a.company_id != b.company_id  # name collision must NOT merge
    assert _company_count(db_session) == 2


def test_cross_identifier_enrichment_links_later_gstin_only_sighting(db_session: Session) -> None:
    # Alpha first seen with BOTH ids (e.g. an MCA record carrying its GSTIN)...
    created = _resolve(
        db_session, CandidateCompany(name="Alpha", cin=CIN_ALPHA, gstin=GST_ALPHA_MH)
    )
    # ...then seen by a GST-only source: must MATCH via the enriched GSTIN, not duplicate.
    gst_only = _resolve(db_session, CandidateCompany(name="Alpha", gstin=GST_ALPHA_MH))
    assert gst_only.disposition is Disposition.MATCHED
    assert gst_only.company_id == created.company_id
    assert _company_count(db_session) == 1


def test_identifier_conflict_is_queued_not_merged(db_session: Session) -> None:
    _resolve(db_session, CandidateCompany(name="Alpha", cin=CIN_ALPHA, gstin=GST_ALPHA_MH))
    _resolve(db_session, CandidateCompany(name="Beta", cin=CIN_BETA, gstin=GST_BETA))
    # A candidate whose CIN is Alpha's but GSTIN is Beta's: two companies, one candidate.
    conflict = _resolve(db_session, CandidateCompany(name="???", cin=CIN_ALPHA, gstin=GST_BETA))
    assert conflict.disposition is Disposition.QUEUED
    assert conflict.method is ResolutionMethod.IDENTIFIER_CONFLICT
    assert _company_count(db_session) == 2  # nothing created or merged
    assert _queue_count(db_session) == 1


def test_same_pan_different_gstin_is_queued_with_hint(db_session: Session) -> None:
    alpha = _resolve(db_session, CandidateCompany(name="Alpha", cin=CIN_ALPHA, gstin=GST_ALPHA_MH))
    # Karnataka registration of the same legal entity (same PAN, different GSTIN).
    other_state = _resolve(db_session, CandidateCompany(name="Alpha KA", gstin=GST_ALPHA_KA))
    assert other_state.disposition is Disposition.QUEUED
    assert other_state.method is ResolutionMethod.PAN_MATCH
    assert _company_count(db_session) == 1  # no duplicate created
    queued = ResolutionRepository(db_session).pending()[0]
    assert queued.candidate_company_id == alpha.company_id  # hinted at the right company


def test_unanchored_single_domain_is_queued_with_hint(db_session: Session) -> None:
    alpha = _resolve(
        db_session,
        CandidateCompany(name="Alpha", cin=CIN_ALPHA, domain="alpha.test"),
    )
    unanchored = _resolve(db_session, CandidateCompany(name="Alpha news", domain="alpha.test"))
    assert unanchored.disposition is Disposition.QUEUED
    assert unanchored.method is ResolutionMethod.DOMAIN_HINT
    assert unanchored.company_id is None  # not auto-resolved
    assert _company_count(db_session) == 1  # unanchored never creates
    assert ResolutionRepository(db_session).pending()[0].candidate_company_id == alpha.company_id


def test_ambiguous_domain_is_queued_without_hint(db_session: Session) -> None:
    _resolve(db_session, CandidateCompany(name="Sub A", cin=CIN_ALPHA, domain="group.test"))
    _resolve(db_session, CandidateCompany(name="Sub B", cin=CIN_BETA, domain="group.test"))
    ambiguous = _resolve(db_session, CandidateCompany(name="Group news", domain="group.test"))
    assert ambiguous.method is ResolutionMethod.AMBIGUOUS_DOMAIN
    assert ResolutionRepository(db_session).pending()[0].candidate_company_id is None


def test_name_only_candidate_is_queued(db_session: Session) -> None:
    result = _resolve(db_session, CandidateCompany(name="Mystery Traders"))
    assert result.disposition is Disposition.QUEUED
    assert result.method is ResolutionMethod.NAME_ONLY
    assert _company_count(db_session) == 0


def test_golden_batch_zero_mismatch_zero_duplicate(db_session: Session) -> None:
    # Three distinct real companies, each observed several times through different
    # sources/identifiers. Every re-sighting carries a linking identifier or is an
    # unanchored/PAN case that must queue (never create). Expected: exactly 3
    # companies, and each identifier resolves to its own company (no cross-merge).
    observations = [
        CandidateCompany(name="Alpha", cin=CIN_ALPHA, gstin=GST_ALPHA_MH),  # create A
        CandidateCompany(name="Alpha", gstin=GST_ALPHA_MH),  # match A (enriched)
        CandidateCompany(name="Alpha KA", gstin=GST_ALPHA_KA),  # queue (PAN) — no create
        CandidateCompany(name="Beta", cin=CIN_BETA),  # create B
        CandidateCompany(name="Beta", cin=CIN_BETA),  # match B (idempotent)
        CandidateCompany(name="Gamma", gstin=GST_BETA),  # create C (distinct PAN)
        CandidateCompany(name="Gamma news", domain="gamma.test"),  # queue (name/domain)
    ]
    results = [_resolve(db_session, obs) for obs in observations]

    created = [r for r in results if r.disposition is Disposition.CREATED]
    assert len(created) == 3  # duplicate rate = 0 (3 distinct → 3 created)
    assert _company_count(db_session) == 3

    # Mismatch rate = 0: the two Alpha ids resolve to the same company; Alpha, Beta,
    # Gamma are pairwise distinct.
    repo = CompanyRepository(db_session)
    alpha = repo.get_by_cin(CIN_ALPHA)
    beta = repo.get_by_cin(CIN_BETA)
    gamma = repo.get_by_gstin(GST_BETA)
    alpha_by_gstin = repo.get_by_gstin(GST_ALPHA_MH)
    assert alpha is not None and beta is not None and gamma is not None
    assert alpha_by_gstin is not None
    assert len({alpha.id, beta.id, gamma.id}) == 3
    assert alpha_by_gstin.id == alpha.id
