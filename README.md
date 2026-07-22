# AI Lead Intelligence Platform

Warm, researched, **evidence-cited Indian-company accounts**, delivered to B2B sellers
targeting the Indian market. We sell the worked conclusion — "why this account, why now,
with proof" — not a database.

The build against [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) started 2026-07-22:
P1-activation scope (full pipeline behind a human QA gate), local Docker Compose only until a
design partner signs. Strategy lives in the living docs under [`docs/`](docs/) — they remain
the source of truth; code follows them.

## Quickstart (dev)

```bash
make sync    # install the uv workspace (needs: uv)
make up      # Postgres 16 + pgvector, MinIO (needs: Docker Desktop)
make test    # run all tests
make lint    # ruff + mypy
```

`make migrate` / `make seed` arrive in later build chunks. Copy `.env.example` → `.env` first.

## Layout

| Path | Contents |
|---|---|
| `docs/` | The living docs — spec, competitor analysis, ADRs, assumptions, risks, questions, roadmap, architecture. Read `docs/PROJECT_SPEC.md` first. |
| `libs/` | Shared Python libraries: `li-core`, `li-db`, `li-queue`, `li-llm`, `li-compliance`, `li-telemetry` |
| `services/` | Pipeline services: `scheduler`, `ingestion`, `resolver`, `agents`, `delivery`, `api` (+ `qa-console`, chunk 5) |
| `.github/workflows/` | CI: ruff, mypy, pytest (Postgres service container) on every PR |

One uv workspace, one lockfile. Python 3.12. Postgres 16 + pgvector is the only database.

## Decision status (ADRs)

| ADR | Decision | Status |
|-----|----------|--------|
| [001](docs/ADR/ADR-001-india-market-leads.md) | Indian-company leads; into-India B2B sellers as customers | ✅ **accepted** |
| [002](docs/ADR/ADR-002-service-before-platform.md) | Productized service before self-serve platform | ✅ **accepted** |
| [003](docs/ADR/ADR-003-signal-phasing.md) | Signal phasing — triggers + deep-fit first; intent/lookalikes deferred | ✅ **accepted** |
| [004](docs/ADR/ADR-004-payper-call-data-apis.md) | Data via pay-per-call registry APIs + own compliant crawling | ✅ **accepted** |
| [005](docs/ADR/ADR-005-company-level-first.md) | Company-level intelligence first; contacts via compliant partners | ✅ **accepted** |

> All five accepted (founder approval 2026-07-16). ADR-003's deferral of lookalikes/intent is
> tracked in `docs/QUESTIONS.md#deferred-signals` with revisit triggers.
> [`docs/ADR/ADR-000-template.md`](docs/ADR/ADR-000-template.md) is the template.

## Conventions

- Cross-references inside `docs/` use the form `FILE.md#anchor` (e.g. `RISKS.md#dpdp`).
- Economics and figures marked as **placeholders** are for validation, not commitments.
- Sourcing: unverified claims carry `[source: internal research — verify]` — never a
  fabricated URL.
- **Compliance is a hard line:** company-level data only (ADR-005). No person-level fields in
  any schema; `li-compliance` gates every fetch.
