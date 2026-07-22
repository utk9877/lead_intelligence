"""DB fixtures. Tests needing Postgres skip unless DATABASE_URL is set (CI sets it).

Ordering note: test_migrations.py runs a full downgrade/upgrade cycle and restores
head at the end; per-test truncation below keeps repository tests independent of it.
"""

from collections.abc import Iterator

import pytest
from alembic import command
from db_test_utils import DATABASE_URL, alembic_config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    assert DATABASE_URL is not None
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def migrated(engine: Engine) -> None:
    command.upgrade(alembic_config(), "head")


@pytest.fixture
def db_session(engine: Engine, migrated: None) -> Iterator[Session]:
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        yield session
        session.rollback()
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE companies, company_identifiers, evidence, signals, "
                "customers, scores, qa_reviews, deliveries, resolution_candidates, "
                "cost_ledger CASCADE"
            )
        )
