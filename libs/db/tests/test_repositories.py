import pytest
from db_test_utils import requires_db
from li_core.errors import InvalidIdentifierError
from li_db.repositories import CompanyRepository
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

pytestmark = requires_db

FICTIONAL_CIN = "U12345MH2019PTC123456"
FICTIONAL_GSTIN = "27ZZZZZ9999Z1Z8"


def test_add_and_lookup_roundtrip(db_session: Session) -> None:
    repo = CompanyRepository(db_session)
    created = repo.add(
        name="Fictional Widgets Pvt Ltd",
        cin=FICTIONAL_CIN,
        gstin=FICTIONAL_GSTIN,
        domain="fictional-widgets.test",
    )
    by_cin = repo.get_by_cin(FICTIONAL_CIN)
    by_gstin = repo.get_by_gstin(FICTIONAL_GSTIN)
    assert by_cin is not None and by_cin.id == created.id
    assert by_gstin is not None and by_gstin.id == created.id
    assert repo.get(created.id) is not None


def test_duplicate_cin_rejected_by_partial_unique_index(db_session: Session) -> None:
    repo = CompanyRepository(db_session)
    repo.add(name="Fictional Widgets Pvt Ltd", cin=FICTIONAL_CIN)
    with pytest.raises(IntegrityError):
        repo.add(name="Impostor Widgets Pvt Ltd", cin=FICTIONAL_CIN)


def test_multiple_companies_without_cin_allowed(db_session: Session) -> None:
    repo = CompanyRepository(db_session)
    repo.add(name="Unregistered Brand One")
    repo.add(name="Unregistered Brand Two")  # NULLs don't collide on the partial index


def test_invalid_identifiers_rejected_at_write_boundary(db_session: Session) -> None:
    repo = CompanyRepository(db_session)
    with pytest.raises(InvalidIdentifierError):
        repo.add(name="Bad CIN Co", cin="NOT-A-CIN")
    with pytest.raises(InvalidIdentifierError):
        repo.add(name="Bad GSTIN Co", gstin="27ZZZZZ9999Z1Z9")  # wrong check char
