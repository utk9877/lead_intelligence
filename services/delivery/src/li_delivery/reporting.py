"""Cost-per-account reporting (tools/cost_report.py renders this).

Economics are placeholders (repo convention) — the report says so in the output.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal


def format_cost_report(by_stage: Mapping[str, Decimal], delivered_accounts: int) -> str:
    total = sum(by_stage.values(), Decimal("0"))
    per_account = (total / delivered_accounts) if delivered_accounts else Decimal("0")
    lines = ["Cost report (illustrative — placeholder economics)", "-" * 48]
    for stage, amount in sorted(by_stage.items()):
        lines.append(f"  {stage:<20} ₹{amount:>12.2f}")
    lines.append("-" * 48)
    lines.append(f"  {'TOTAL':<20} ₹{total:>12.2f}")
    lines.append(f"  delivered accounts   {delivered_accounts:>13}")
    lines.append(f"  {'₹/account':<20} ₹{per_account:>12.2f}")
    return "\n".join(lines)
