"""Reusable test helpers so any service's tests can spin up a migrated database.

Kept in the library (not a test dir) so it is importable across packages. Only
used by tests, but harmless in prod (imports nothing heavy at module load).
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# libs/db/alembic.ini — script_location inside it is %(here)s-relative, so cwd-independent.
ALEMBIC_INI = Path(__file__).parents[2] / "alembic.ini"

_ALL_TABLES = (
    "companies",
    "company_identifiers",
    "evidence",
    "signals",
    "customers",
    "scores",
    "qa_reviews",
    "deliveries",
    "resolution_candidates",
    "cost_ledger",
)


def database_url() -> str | None:
    return os.environ.get("DATABASE_URL")


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def make_engine(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def migrate_to_head() -> None:
    command.upgrade(alembic_config(), "head")


def truncate_all(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {', '.join(_ALL_TABLES)} CASCADE"))


@contextmanager
def clean_session(engine: Engine) -> Iterator[Session]:
    """A session that is rolled back and whose tables are truncated afterwards, so
    each test starts from an empty graph."""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        with factory() as session:
            yield session
            session.rollback()
    finally:
        truncate_all(engine)
