"""Schema-level compliance policy (ADR-005): runs without a database.

If a migration/model ever adds a person-shaped column, this fails CI. Never
weaken this list to make a build pass — that is the compliance boundary moving.
"""

from li_db.orm import Base

FORBIDDEN_COLUMN_SUBSTRINGS = (
    "email",
    "phone",
    "mobile",
    "first_name",
    "last_name",
    "full_name",
    "person",
    "contact_",
    "linkedin",
    "date_of_birth",
    "aadhaar",
    "aadhar",
)


def test_no_person_shaped_columns_anywhere() -> None:
    violations = [
        f"{table.name}.{column.name}"
        for table in Base.metadata.tables.values()
        for column in table.columns
        if any(bad in column.name.lower() for bad in FORBIDDEN_COLUMN_SUBSTRINGS)
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
