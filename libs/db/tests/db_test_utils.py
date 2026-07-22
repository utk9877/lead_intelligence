import os
from pathlib import Path

import pytest
from alembic.config import Config

DATABASE_URL = os.environ.get("DATABASE_URL")

requires_db = pytest.mark.skipif(
    DATABASE_URL is None, reason="DATABASE_URL not set (Postgres integration tests)"
)

ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))
