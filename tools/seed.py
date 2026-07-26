"""Seed fictional dev companies into the database.

FICTIONAL DATA ONLY — obviously fake names, never real records (docs/ARCHITECTURE.md
§5 seed rule). Run against a local/dev DATABASE_URL: `uv run python tools/seed.py`.
"""

from __future__ import annotations

from li_db.repositories import CompanyRepository
from li_db.session import create_engine_from_settings, create_session_factory

# Structurally valid, deliberately fictional (registration numbers are obviously fake).
FICTIONAL_COMPANIES = [
    {
        "name": "Fictional Widgets Pvt Ltd",
        "cin": "U12345MH2019PTC100001",
        "domain": "fictional-widgets.test",
    },
    {
        "name": "Imaginary Analytics Pvt Ltd",
        "cin": "U12345KA2020PTC100002",
        "domain": "imaginary-analytics.test",
    },
    {
        "name": "Placeholder Logistics Pvt Ltd",
        "cin": "U12345DL2018PTC100003",
        "domain": "placeholder-logistics.test",
    },
]


def main() -> None:  # pragma: no cover - dev script
    engine = create_engine_from_settings()
    with create_session_factory(engine)() as session:
        repo = CompanyRepository(session)
        for company in FICTIONAL_COMPANIES:
            repo.add(**company)
        session.commit()
    print(f"seeded {len(FICTIONAL_COMPANIES)} fictional companies")


if __name__ == "__main__":  # pragma: no cover
    main()
