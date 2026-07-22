from alembic import command
from db_test_utils import alembic_config, requires_db
from sqlalchemy import Engine, inspect

pytestmark = requires_db

EXPECTED_TABLES = {
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
}


def test_upgrade_creates_all_tables(engine: Engine, migrated: None) -> None:
    tables = set(inspect(engine).get_table_names())
    missing = EXPECTED_TABLES - tables
    assert not missing, f"missing tables after upgrade: {missing}"


def test_partial_unique_indexes_exist(engine: Engine, migrated: None) -> None:
    index_names = {index["name"] for index in inspect(engine).get_indexes("companies")}
    assert {"uq_companies_cin", "uq_companies_gstin"} <= index_names


def test_no_model_migration_drift(migrated: None) -> None:
    """`alembic check`: the ORM models and the migration chain must agree."""
    command.check(alembic_config())


def test_full_downgrade_then_restore(engine: Engine, migrated: None) -> None:
    config = alembic_config()
    command.downgrade(config, "base")
    tables = set(inspect(engine).get_table_names())
    assert not (EXPECTED_TABLES & tables), "downgrade left tables behind"
    command.upgrade(config, "head")
    assert set(inspect(engine).get_table_names()) >= EXPECTED_TABLES
