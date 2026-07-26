"""Print the cost-per-account report from the cost ledger.

`uv run python tools/cost_report.py`. Economics are placeholders (the report says
so). Cost-per-account is the unit economic the whole model rests on (PROJECT_SPEC §6).
"""

from __future__ import annotations

from li_db.repositories import CostLedgerRepository, DeliveryRepository
from li_db.session import create_engine_from_settings, create_session_factory
from li_delivery.reporting import format_cost_report


def main() -> None:  # pragma: no cover - dev script
    engine = create_engine_from_settings()
    with create_session_factory(engine)() as session:
        by_stage = CostLedgerRepository(session).by_stage()
        delivered = DeliveryRepository(session).count()
    print(format_cost_report(by_stage, delivered))


if __name__ == "__main__":  # pragma: no cover
    main()
