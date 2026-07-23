"""DB-backed fixtures for resolver tests; skip unless DATABASE_URL is set (CI)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from li_db.testing import clean_session, database_url, make_engine, migrate_to_head
from sqlalchemy import Engine
from sqlalchemy.orm import Session

requires_db = pytest.mark.skipif(
    database_url() is None, reason="DATABASE_URL not set (Postgres integration tests)"
)


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url = database_url()
    assert url is not None
    engine = make_engine(url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def migrated(engine: Engine) -> None:
    migrate_to_head()


@pytest.fixture
def db_session(engine: Engine, migrated: None) -> Iterator[Session]:
    with clean_session(engine) as session:
        yield session
