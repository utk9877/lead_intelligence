"""Dependency providers. Tests override `get_service` with an in-memory fake, so
routers are unit-testable without a database."""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from li_db.session import create_engine_from_settings, create_session_factory
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from li_api.service import DbQaService, QaService


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    engine: Engine = create_engine_from_settings()
    return create_session_factory(engine)


def get_session() -> Iterator[Session]:  # pragma: no cover - exercised via DbQaService
    with _session_factory()() as session:
        yield session


def get_service() -> Iterator[QaService]:  # pragma: no cover - overridden in unit tests
    with _session_factory()() as session:
        yield DbQaService(session)
