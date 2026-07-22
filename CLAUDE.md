# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this
repository.

## What this repository is

The monorepo for **Lead Intelligence** — an AI lead-intelligence platform delivering warm,
researched, evidence-cited *Indian company* accounts to B2B sellers targeting India.

Two layers, one repo:

1. **`docs/` — the living strategy docs.** Spec, competitor analysis, ADRs, assumptions,
   risks, open questions, roadmap, architecture blueprint. They are the source of truth;
   code follows them. Changing one usually obliges updating the docs that reference it.
2. **Code — a uv workspace** (Python 3.12) being built against `docs/ARCHITECTURE.md` in
   chunks (build started 2026-07-22). Scope is **P1 activation only**: full pipeline behind a
   human QA gate, local Docker Compose, **no AWS/Kubernetes until a design partner signs**
   (`docs/ROADMAP.md#design-partner`). Don't build ahead of the phase gates.

## Commands

```bash
make sync       # uv sync --all-packages
make test       # pytest across libs/ and services/
make lint       # ruff check + format check + mypy (strict)
make fmt        # auto-format
make up/down    # docker compose: Postgres 16 + pgvector, MinIO (requires Docker Desktop)
make migrate    # Alembic — arrives chunk 1
make seed       # fictional seed data — arrives chunk 6
```

Run a single test: `uv run pytest libs/core/tests/test_li_core_import.py -q`.
CI (`.github/workflows/ci.yml`) runs lint + tests (Postgres service container) on every PR
and on `build/**` branches; nothing merges red.

## Build workflow (chunked, agent-reviewed)

The approved build plan is 7 chunks: 0 scaffold/CI → 1 libs+DB → 2 ingestion+snapshots →
3 resolver → 4 li-llm + 3-pass agents → 5 API + QA console → 6 delivery + e2e smoke →
7 AWS (only when a design partner signs). Each chunk: branch `build/chunk-N-<name>` →
implement with tests → independent testing-agent pass (adversarial tests from spec) →
review pass, fix until zero confirmed findings → PR → CI green → merge.

## Architecture (see docs/ARCHITECTURE.md for the full blueprint)

`scheduler → ingestion (source adapters, evidence snapshots) → resolver (CIN/GSTIN anchoring)
→ agents (3-pass: trigger classify / deep-fit research / rubric scoring) → QA console (human
gate) → delivery (Slack/CRM)`. Every arrow is a queue boundary (Procrastinate on Postgres).
One Postgres 16 + pgvector database holds the company graph, job queue, cost ledger, and
embeddings. Evidence pages are snapshotted immutably to MinIO/S3 — citations never dangle.
Shared libs (`li-core`, `li-db`, `li-queue`, `li-llm`, `li-compliance`, `li-telemetry`) are
imported, never networked.

## The accepted decisions that constrain all work

Contradicting one requires a new ADR, not an edit in passing (`docs/ADR/`, all accepted
2026-07-16):

- **ADR-001** — Indian companies as leads; registry anchoring on CIN/GSTIN is the moat.
- **ADR-002** — Productized service before self-serve platform. The internal QA console is
  the only UI; customers get delivery, not logins.
- **ADR-003** — Two signal types only: buying triggers + deep-fit reasoning. Lookalikes and
  third-party intent are deferred (`docs/QUESTIONS.md#deferred-signals`).
- **ADR-004** — Pay-per-call registry APIs + own compliant crawling; no enterprise licenses.
  Registry vendor is unchosen (`docs/QUESTIONS.md#api-vendor`) — vendor adapters stay
  fixture-stubbed behind the adapter interface until it is.
- **ADR-005** — **Company-level intelligence only.** The hard line below.

## Non-obvious conventions you must follow

**The compliance boundary is a hard line (ADR-005, `docs/RISKS.md#dpdp`, `#data-tos`).**
Never propose scraping LinkedIn/Naukri or any person-level data. Job posts are used at the
*posting* level only — adapter output types must have no name/email fields. No person-level
columns in any migration (schema review is the enforcement point). Every fetcher passes
`li-compliance.allowed_sources`; tests that assert these rejections are CI-load-bearing —
never weaken them to make a build pass.

**Sourcing discipline (docs).** Unverified claims carry the literal marker
`[source: internal research — verify]`. Never fabricate a URL or citation. In code, the same
rule is structural: a claim that doesn't join an evidence row must fail rendering.

**Economics are placeholders.** All pricing/cost/margin figures in `docs/` are unvalidated;
anywhere they surface they must be visibly marked illustrative. The real number comes from
the cost ledger (`li-llm/ledger.py` when it lands), not estimates.

**Cross-references in `docs/` use `FILE.md#anchor`** — the docs are deliberately flat
siblings in `docs/` so those links hold. Explicit anchors like `{#dpdp}` are link targets;
grep before renaming. ADR status lives in three places (ADR front-matter, its status-history
section, the README decision table) — a status change edits all of them.

**Gate discipline (`docs/ROADMAP.md`).** Phases advance on learning + revenue gates, never
time. Deliberately not built now: Kubernetes/EKS, Terraform apply, SQS driver, CRM auto-sync,
customer-facing UI, Prometheus/Grafana, lookalikes/intent. The K8s/Terraform *designs* in
ARCHITECTURE.md stay design until their gates.

**Seed/fixture data is fictional only** — obviously fake companies, never real records.

## Generated deliverables

PDFs (e.g. `Lead_Intelligence_Companion_Analysis.pdf`) are gitignored derived artifacts,
regenerated from Markdown via headless Chrome when strategy stabilizes:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="<output>.pdf" "<source>.html"
```

Markdown remains the source of truth; update docs first, then regenerate.
