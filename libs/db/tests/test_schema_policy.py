"""Schema-level compliance policy (ADR-005): runs without a database.

If a migration/model ever adds a person-shaped column, this fails CI. Never
weaken this list to make a build pass — that is the compliance boundary moving.
"""

from li_db.orm import Base

# Kept in step with li_compliance.guards: what that library rejects at the ingest
# boundary, the schema must reject as a column. Substrings catch snake_case columns;
# short exact tokens (din/dob/ceo…) would false-positive as substrings (coordinates,
# random_dob…) so they match a normalized column name exactly.
FORBIDDEN_COLUMN_SUBSTRINGS = (
    "email",
    "phone",
    "mobile",
    "whatsapp",
    "first_name",
    "last_name",
    "middle_name",
    "full_name",
    "person",
    "contact_name",
    "contact_person",
    "linkedin",
    "designation",
    "director",
    "founder",
    "date_of_birth",
    "aadhaar",
    "aadhar",
)
FORBIDDEN_COLUMN_EXACT = frozenset({"din", "dob", "ceo", "cfo", "cto", "name_of_director"})


def _normalize_column(name: str) -> str:
    return name.lower()


def test_no_person_shaped_columns_anywhere() -> None:
    violations = [
        f"{table.name}.{column.name}"
        for table in Base.metadata.tables.values()
        for column in table.columns
        if (norm := _normalize_column(column.name)) in FORBIDDEN_COLUMN_EXACT
        or any(bad in norm for bad in FORBIDDEN_COLUMN_SUBSTRINGS)
    ]
    assert violations == [], f"person-shaped columns found (ADR-005): {violations}"


def test_signals_always_cite_evidence() -> None:
    signals = Base.metadata.tables["signals"]
    assert signals.columns["evidence_id"].nullable is False


def test_nothing_delivered_without_qa() -> None:
    deliveries = Base.metadata.tables["deliveries"]
    assert deliveries.columns["qa_review_id"].nullable is False


def test_append_only_tables_have_no_updated_at() -> None:
    for table_name in ("qa_reviews", "deliveries", "cost_ledger"):
        columns = set(Base.metadata.tables[table_name].columns.keys())
        assert "updated_at" not in columns, f"{table_name} must stay append-only"
