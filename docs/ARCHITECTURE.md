# Architecture — Implementation Design

> **Status:** implementation blueprint; the build against it began 2026-07-22 (chunked build
> plan, P1-activation scope, local-only until a design partner signs).
> This document is the implementation-level blueprint the build phases code against:
> service decomposition, the full monorepo tree, container/Kubernetes design, and the AWS
> hosting path. It elaborates the P2 pipeline sketch in `ROADMAP.md` and §3 of the Companion
> Analysis; it locks nothing — deviations get recorded as ADRs.
> **Phasing honesty:** everything below is *designed* now but *activated* per phase gate.
> A duo team runs Docker Compose on one instance at P1; Kubernetes/EKS activates only at the
> P2 gate (ASSUMPTIONS.md#delivery-capacity, RISKS.md#bus-factor).

---

## 1. System overview

```
                        ┌─────────────────────────────────────────────────────────────┐
                        │                    SOURCES (public, company-level only)     │
                        │  MCA/GST registry APIs · careers pages · job boards ·       │
                        │  news/funding feeds · company sites (tech-detect)           │
                        └────────────┬────────────────────────────────────────────────┘
                                     │ every fetch passes the compliance gate (libs/compliance)
                                     ▼
┌──────────────┐   jobs   ┌──────────────────┐  candidates  ┌──────────────────┐
│  scheduler   │ ───────▶ │  ingestion svc   │ ───────────▶ │   resolver svc   │
│ (singleton)  │          │  source adapters │              │ CIN/GSTIN anchor │
└──────────────┘          └────────┬─────────┘              └────────┬─────────┘
                                   │ raw artifacts                   │ resolved entities
                                   ▼                                 ▼
                          ┌─────────────────────────────────────────────────┐
                          │        COMPANY GRAPH — Postgres 16 + pgvector   │
                          │  companies · identifiers · signals · evidence · │
                          │  scores · customers · deliveries · qa_reviews   │
                          │  + job queue tables + cost ledger               │
                          └───────┬─────────────────────────────┬───────────┘
                                  │                             │
              evidence snapshots  ▼                             ▼  three-pass pipeline
                          ┌──────────────┐              ┌──────────────────┐
                          │ object store │◀─────────────│    agents svc    │
                          │ (MinIO → S3) │  page snaps  │ pass1 triggers   │
                          └──────────────┘              │ pass2 deep-fit   │
                                                        │ pass3 scoring    │
                                                        └────────┬─────────┘
                                                                 │ scored, evidence-cited
                                                                 ▼
                          ┌──────────────┐   approved   ┌──────────────────┐
                          │  qa-console  │ ───────────▶ │   delivery svc   │
                          │ (human gate) │              │ Slack · CRM sync │
                          └──────────────┘              └──────────────────┘
```

Every arrow is a **queue boundary** (idempotent jobs, per-stage cost metering, retries).
Nothing reaches a customer except through the QA gate. Every fetch passes the compliance
gate — the allowed-sources list of RISKS.md#data-tos is *code*, not a wiki page.

## 2. Service decomposition

| Service | Responsibility | Scaling shape | Runtime |
|---|---|---|---|
| `scheduler` | Cron-style planning: which companies/sources to refresh, per-customer batch cadence | **Singleton** (leader-elected in K8s) | Python |
| `ingestion` | Source adapters: registry API clients, compliant crawlers (Playwright), news/funding ingest; writes raw artifacts + normalized candidates | Horizontal — per-source worker pools | Python |
| `resolver` | Entity resolution onto CIN/GSTIN anchors; secondary-identifier fallback (GSTIN-only, domain, marketplace); queues ambiguous cases for human merge | Horizontal | Python |
| `agents` | Three-pass pipeline: trigger detection (small model) → deep-fit research (frontier model, tool loop) → warm scoring (mid model, fixed rubric); enforces per-account budget caps | Horizontal — the main compute consumer | Python |
| `delivery` | Renders account cards (claims joined to evidence), Slack webhooks, CRM (HubSpot/Zoho) sync, feedback capture | Horizontal, low volume | Python |
| `api` | Internal REST API over the graph (FastAPI): powers qa-console; becomes the P3 customer-facing surface behind auth | Horizontal | Python/FastAPI |
| `qa-console` | Reviewer UI: approve/reject/edit per account, evidence inspection, merge resolution queue | Stateless web | Next.js |

**Shared libraries** (imported, never networked — a duo does not run a service mesh):
`li-core` (domain models, config), `li-db` (SQLAlchemy + Alembic, repositories), `li-queue`
(job-queue abstraction), `li-llm` (Claude client, model tiering, prompt caching, cost ledger),
`li-compliance` (allowed-sources registry, robots policy, person-data guards), `li-telemetry`
(structured logs, OpenTelemetry, metrics).

## 3. Data architecture

- **Postgres 16 + pgvector — one database, four concerns:** the company graph (schema in
  Companion Analysis §3.2), the **job queue** (Procrastinate — Postgres-backed, no broker to
  operate), the **cost ledger** (every LLM/API call row-logged with account attribution — the
  cost-per-account metric of PROJECT_SPEC.md §6 is a SQL query, not a spreadsheet), and
  **embeddings** (company profiles, fit-similarity features).
- **Object store for evidence snapshots:** every cited page is snapshotted at capture time
  (content-hash keyed, immutable) so citations survive source pages changing or dying.
  MinIO in local dev → S3 in AWS. `evidence.source_url` + `evidence.content_hash` always
  resolve to a stored snapshot.
- **No person-level fields anywhere in the schema** (ADR-005). Schema reviews are the
  enforcement point: a migration adding person fields fails review by policy.
- **Caching:** registry responses (~30-day TTL per CIN/GSTIN), crawl content-hash dedupe,
  Anthropic prompt caching on stable customer-ICP preambles, embedding reuse.
- **Queue → SQS portability:** `li-queue` exposes enqueue/claim/complete; Procrastinate is the
  P1/P2 driver, an SQS driver is the P3 option if scale demands it. Services never import the
  driver directly.

## 4. Monorepo directory tree

One repository. The living docs move under `docs/` when code lands (they remain the strategy
source of truth; this file moves with them). Python is managed as a **uv workspace**
(root `pyproject.toml` + per-package members); one lockfile, one venv, atomic cross-cutting
changes — right for a duo.

```
lead-intelligence/
├── README.md
├── CLAUDE.md
├── Makefile                          # dev entrypoints: make up, test, lint, migrate, seed
├── pyproject.toml                    # uv workspace root; ruff + pytest config
├── uv.lock
├── .env.example                      # every env var documented; no secrets committed
├── .pre-commit-config.yaml
├── docker-compose.yml                # full local stack (see §5)
├── docker-compose.override.yml.example
│
├── .github/
│   └── workflows/
│       ├── ci.yml                    # lint, typecheck, tests, migration check (every PR)
│       ├── build-push.yml            # build images → ECR on main merge
│       └── deploy.yml                # staging auto, prod on tag (see §8)
│
├── docs/                             # ← the living docs, flat so FILE.md#anchor links hold
│   ├── PROJECT_SPEC.md · ROADMAP.md · ASSUMPTIONS.md · RISKS.md · QUESTIONS.md
│   ├── COMPETITOR_ANALYSIS.md
│   ├── ARCHITECTURE.md               # this document
│   └── ADR/
│
├── libs/
│   ├── core/                         # li-core
│   │   ├── pyproject.toml
│   │   └── src/li_core/
│   │       ├── config.py             # pydantic-settings; env-driven, no config files in prod
│   │       ├── ids.py                # CIN/GSTIN parsing + validation (checksum rules)
│   │       ├── models/               # pure domain dataclasses (no ORM here)
│   │       │   ├── company.py
│   │       │   ├── signal.py         # the six trigger types — enum mirrors PROJECT_SPEC §4
│   │       │   ├── evidence.py
│   │       │   └── score.py
│   │       └── errors.py
│   ├── db/                           # li-db
│   │   ├── pyproject.toml
│   │   └── src/li_db/
│   │       ├── orm/                  # SQLAlchemy models (graph + ops tables)
│   │       ├── repositories/         # all SQL behind repository interfaces
│   │       ├── migrations/           # Alembic; partial unique indexes on cin/gstin live here
│   │       └── session.py
│   ├── queue/                        # li-queue
│   │   └── src/li_queue/
│   │       ├── interface.py          # enqueue/claim/complete/fail — driver-agnostic
│   │       ├── procrastinate_driver.py
│   │       └── sqs_driver.py         # P3 option; exists as interface-proof, not used at P1
│   ├── llm/                          # li-llm
│   │   └── src/li_llm/
│   │       ├── client.py             # Anthropic SDK wrapper; retries, timeouts
│   │       ├── tiers.py              # pass→model mapping (small/frontier/mid) in ONE place
│   │       ├── prompt_cache.py
│   │       ├── budget.py             # per-account hard caps; kills runaway agent loops
│   │       └── ledger.py             # writes cost_ledger rows: tokens, ₹, account, pass
│   ├── compliance/                   # li-compliance — RISKS.md#data-tos as code
│   │   └── src/li_compliance/
│   │       ├── allowed_sources.py    # THE allowlist; every fetcher must pass it
│   │       ├── robots.py             # robots.txt honoring for crawlers
│   │       └── guards.py             # person-data pattern rejection at ingest boundary
│   └── telemetry/                    # li-telemetry
│       └── src/li_telemetry/
│           ├── logging.py            # structlog JSON
│           ├── tracing.py            # OpenTelemetry setup
│           └── metrics.py            # Prometheus exporters
│
├── services/
│   ├── scheduler/
│   │   ├── Dockerfile
│   │   └── src/li_scheduler/
│   │       ├── main.py
│   │       ├── plans.py              # refresh cadences per source/customer batch
│   │       └── leader.py             # K8s lease-based leader election (no-op under Compose)
│   ├── ingestion/
│   │   ├── Dockerfile
│   │   └── src/li_ingestion/
│   │       ├── main.py               # queue worker entrypoint
│   │       ├── adapters/
│   │       │   ├── base.py           # Adapter ABC: fetch → raw artifact → normalize
│   │       │   ├── registry_mca.py   # MCA company master data (pay-per-call vendor client)
│   │       │   ├── registry_gst.py   # GSTIN verification/monitoring
│   │       │   ├── careers_pages.py  # Playwright; posting-level ONLY (hiring signal)
│   │       │   ├── job_boards.py     # posting-level ONLY — never person records
│   │       │   ├── news_funding.py
│   │       │   └── site_tech.py      # tech-detect from company sites
│   │       ├── snapshots.py          # evidence snapshot writer (object store)
│   │       └── normalize.py          # raw → candidate entities/signals
│   ├── resolver/
│   │   ├── Dockerfile
│   │   └── src/li_resolver/
│   │       ├── main.py
│   │       ├── anchor.py             # CIN/GSTIN hard-anchor resolution
│   │       ├── fallback.py           # GSTIN-only / domain / marketplace (Q5 edge cases)
│   │       └── merge_queue.py        # ambiguous → resolution_candidates for human merge
│   ├── agents/
│   │   ├── Dockerfile
│   │   └── src/li_agents/
│   │       ├── main.py
│   │       ├── pass1_triggers/
│   │       │   ├── classify.py       # batch classification, small model
│   │       │   └── prompts/
│   │       ├── pass2_research/
│   │       │   ├── harness.py        # direct Claude tool-use loop; no heavy framework
│   │       │   ├── tools/            # graph_lookup, site_fetch, registry_fetch, snapshot_read
│   │       │   └── prompts/          # versioned; prompt changes bump scores.model_version
│   │       ├── pass3_scoring/
│   │       │   ├── rubric.py         # fixed scoring rubric, mid model
│   │       │   └── prompts/
│   │       └── evidence.py           # claims MUST join evidence rows or rendering fails
│   ├── delivery/
│   │   ├── Dockerfile
│   │   └── src/li_delivery/
│   │       ├── main.py
│   │       ├── cards.py              # account-card renderer (why-this / why-now + citations)
│   │       ├── slack.py
│   │       ├── crm/
│   │       │   ├── hubspot.py
│   │       │   └── zoho.py
│   │       └── feedback.py           # customer feedback → deliveries (the labelled data)
│   ├── api/
│   │   ├── Dockerfile
│   │   └── src/li_api/
│   │       ├── main.py               # FastAPI app
│   │       ├── auth.py               # internal auth P1/P2; customer auth at P3
│   │       └── routers/              # companies, signals, scores, qa, deliveries, costs
│   └── qa-console/
│       ├── Dockerfile
│       ├── package.json              # Next.js + TypeScript
│       └── src/
│           ├── app/                  # review queue, account detail, merge queue, cost board
│           └── components/
│
├── deploy/
│   ├── docker/
│   │   └── python-base.Dockerfile    # shared slim base: uv, non-root user, tini
│   ├── k8s/                          # designed now; ACTIVATED AT P2 GATE (see §6)
│   │   ├── base/
│   │   │   ├── namespace.yaml
│   │   │   ├── scheduler.yaml        # Deployment replicas:1 + Lease leader election
│   │   │   ├── ingestion.yaml       │
│   │   │   ├── resolver.yaml        │ Deployments + HPA per worker service
│   │   │   ├── agents.yaml          │
│   │   │   ├── delivery.yaml        │
│   │   │   ├── api.yaml              # Deployment + Service + Ingress
│   │   │   ├── qa-console.yaml
│   │   │   ├── migrate-job.yaml      # Alembic as a pre-deploy Job
│   │   │   ├── networkpolicy.yaml    # egress allowlist mirrors li-compliance sources
│   │   │   ├── external-secrets.yaml # ExternalSecrets → AWS Secrets Manager
│   │   │   └── kustomization.yaml
│   │   └── overlays/
│   │       ├── staging/              # small replicas, staging DB, fake delivery targets
│   │       └── prod/
│   └── terraform/                    # AWS IaC; STATE ONLY, nothing applied at Phase 0
│       ├── modules/
│       │   ├── network/              # VPC, private subnets, NAT, ap-south-1 (see §7)
│       │   ├── rds/                  # Postgres 16 + pgvector, backups, PITR
│       │   ├── s3/                   # evidence-snapshots bucket (versioned, lifecycle)
│       │   ├── ecr/
│       │   ├── eks/                  # cluster + managed node group + Karpenter (P2)
│       │   ├── ec2-compose/          # P1: one instance running the Compose stack
│       │   ├── iam/                  # IRSA roles per service, least-privilege
│       │   └── secrets/              # Secrets Manager entries + rotation
│       └── envs/
│           ├── staging/
│           └── prod/
│
├── ops/
│   ├── runbooks/                     # delivery-week runbook, incident, vendor-quota,
│   │   └── …                         #   DPDP-gate checklist (RISKS.md#dpdp review)
│   └── dashboards/                   # Grafana JSON: pipeline health, cost/account, precision
│
└── tools/
    ├── seed.py                       # fixture companies for local dev (fictional data only)
    ├── cost_report.py                # cost ledger → per-account/per-customer report
    └── eval/                         # scoring eval harness: replay delivered accounts
        └── precision_report.py       #   against customer feedback (precision-of-warm)
```

## 5. Local development — Docker Compose

`docker-compose.yml` runs the entire system on a laptop; parity with prod is the point.

| Container | Image/build | Notes |
|---|---|---|
| `postgres` | `pgvector/pgvector:pg16` | graph + queue + ledger; volume-persisted |
| `minio` | `minio/minio` | S3-compatible evidence store; same client code as AWS |
| `scheduler` / `ingestion` / `resolver` / `agents` / `delivery` / `api` | built from `services/*/Dockerfile` | hot-reload via bind mounts in the override file |
| `qa-console` | Next.js dev server | |
| `otel-collector` + `grafana` + `prometheus` | optional profile `observability` | same dashboards as prod |

Workflow: `make up` → `make migrate` → `make seed` (fictional companies only — the seed data
rule follows the worked-example rule: obviously fake, never real records) → run any pass
against seeds. `ANTHROPIC_API_KEY` in `.env`; per-account budget caps default LOW locally.

## 6. Kubernetes design (activated at the P2 gate)

Manifests are **Kustomize** (base + overlays; less machinery than Helm for a two-person team —
Helm is a P3 revisit if charts need external consumers).

- **Workloads:** each worker service is a Deployment scaled by an HPA on queue-depth custom
  metrics; `scheduler` is a single-replica Deployment with Lease-based leader election;
  Alembic migrations run as a pre-deploy Job; `api`/`qa-console` sit behind one Ingress
  (ALB controller) with the console auth-gated.
- **NetworkPolicy mirrors compliance:** default-deny egress; the egress allowlist is generated
  from `li-compliance/allowed_sources.py` so the cluster *cannot* fetch from a source the
  policy layer hasn't approved. The compliance gate exists twice — in code and in the network.
- **Secrets:** External Secrets Operator → AWS Secrets Manager. No secret ever in a manifest.
- **Why not K8s at P1:** one Compose host is one thing to operate; a cluster is twenty. The
  P1→P2 gate (human-minutes/account down, precision held) is also the signal that worker
  parallelism — the thing K8s is actually for here — has become the constraint.

## 7. AWS hosting path

**Region: `ap-south-1` (Mumbai).** Data residency in-country simplifies the DPDP posture
(RISKS.md#dpdp) and keeps latency to registry vendors low. All figures/choices below are
design intent — provider decisions get finalized against real quotas and pricing at build time.

```
Phase P1 — one box, managed data:            Phase P2+ — EKS:
┌─────────────────────────────┐              ┌──────────────────────────────────┐
│ EC2 (t4g.large, Compose)    │              │ EKS + managed nodes / Karpenter  │
│  all services + console     │              │  Deployments + HPA (see §6)      │
├─────────────────────────────┤              ├──────────────────────────────────┤
│ RDS Postgres 16 (pgvector)  │──unchanged──▶│ RDS Postgres 16 (scaled up)      │
│ S3 evidence bucket          │──unchanged──▶│ S3 evidence bucket               │
│ Secrets Manager · ECR       │──unchanged──▶│ Secrets Manager · ECR · IRSA     │
│ CloudWatch logs             │              │ Prometheus/Grafana + CloudWatch  │
└─────────────────────────────┘              └──────────────────────────────────┘
```

- **From day one (P1):** RDS (backups/PITR beat self-hosted Postgres from the first customer),
  S3 for evidence snapshots, ECR for images, Secrets Manager, a single EC2 instance running
  the Compose stack via the `ec2-compose` Terraform module. Route53 + ALB in front of api/console.
- **The P2 move is additive, not a rewrite:** RDS, S3, ECR, Secrets carry over unchanged; the
  Compose host is replaced by the EKS module + the `deploy/k8s/` manifests that have existed
  (and been exercised in staging) since P1. Images are identical.
- **LLM traffic:** direct Anthropic API by default; **AWS Bedrock in ap-south-1 is the
  fallback lane** if data-residency requirements harden — `li-llm/client.py` is the single
  seam where that swap happens.
- **Cost posture:** the P1 footprint is a few thousand ₹/month of infrastructure — deliberately
  trivial next to the LLM + registry per-account costs the cost ledger tracks
  (ASSUMPTIONS.md#api-cost). Infra never becomes the reason the margin breaks.

## 8. CI/CD

1. **PR:** ruff + mypy + pytest (unit; integration against ephemeral Postgres service
   container) + Alembic drift check + `li-compliance` policy tests. Frontend: lint + build.
2. **Merge to main:** build all service images (multi-arch, arm64-first for Graviton), push to
   ECR tagged with git SHA; deploy to **staging** (Compose host at P1, staging overlay at P2);
   run smoke: enqueue a seed company end-to-end through pass 1–3 against a stub LLM.
3. **Release tag:** deploy to prod. Migrations run as the pre-deploy step; rollback = redeploy
   previous SHA (migrations are always backwards-compatible one release — enforced in review).

## 9. Security & compliance-by-design

| Control | Mechanism |
|---|---|
| Company-level only (ADR-005) | No person fields in schema (migration review policy); `li-compliance.guards` rejects person-shaped payloads at the ingest boundary |
| Allowed sources (RISKS.md#data-tos) | `allowed_sources.py` gates every fetcher; K8s egress NetworkPolicy generated from the same list |
| Posting-level hiring signals | `careers_pages.py` / `job_boards.py` normalize to posting counts/roles — no name/email fields exist in their output types |
| Evidence integrity | Immutable content-hash snapshots in S3 (versioned bucket); citations never dangle |
| Secrets | Secrets Manager + IRSA; nothing in env files beyond local dev |
| Audit | Append-only `qa_reviews` + `deliveries`; cost ledger doubles as an API-usage audit trail |
| DPDP calendar | Nov 2026 enforcement / May 2027 full-compliance checkpoints in the phase-gate runbook (Companion Analysis §2.3) |

## 10. Observability & the metrics that matter

Three dashboards, matching PROJECT_SPEC.md §6 — not generic infra graphs:

1. **Pipeline health:** queue depths, per-stage throughput/error rates, adapter freshness
   (staleness per source is the leading indicator of silent quality decay — Companion §3.5).
2. **Unit economics:** cost ledger rollups — ₹/account by pass, by customer, by model tier;
   alert when a single account breaches its budget cap.
3. **Quality:** precision-of-warm from `deliveries` feedback by `model_version`; QA reject
   rate; human-minutes/account (console-instrumented) — the P1→P2 gate metrics, live.

## 11. Phase activation matrix

| Capability | P1 (manual + agents) | P2 (productized) | P3 (self-serve) |
|---|---|---|---|
| Compute | One EC2 + Compose | EKS (Kustomize overlays) | EKS + Karpenter autoscale |
| Queue | Procrastinate (Postgres) | Procrastinate | Procrastinate or SQS driver |
| Scheduler | cron on host | Lease-elected singleton | same |
| QA console | minimal review queue | + merge queue, cost board | + customer-facing app (api grows auth) |
| Delivery | Slack (manual send OK) | Slack + CRM sync automated | customer-configured |
| Observability | CloudWatch + cost ledger | + Prometheus/Grafana stack | same |
| Terraform applied | network, rds, s3, ecr, iam, secrets, ec2-compose | + eks | + scale modules |

## 12. Open technical decisions

Tracked here so nothing is silently assumed (QUESTIONS.md discipline):

- **T1 — Registry vendor client shape:** one adapter per vendor vs a vendor-neutral facade —
  decided by the P0 vendor comparison outcome (QUESTIONS.md#api-vendor).
- **T2 — Crawl scale tooling:** Playwright-per-worker is fine to ~10³ pages/day; if a chosen
  niche needs more, evaluate a crawl frontier service *then*, not preemptively.
- **T3 — Queue metrics for HPA:** custom-metrics adapter vs KEDA at P2 — pick when EKS lands.
- **T4 — Bedrock vs direct API:** revisit if DPDP guidance hardens on cross-border inference
  (§7); the `li-llm` seam keeps this a one-file decision.
- **T5 — Eval harness depth:** how much of `tools/eval` is built at P1 vs P2 — minimum at P1
  is the precision report per model_version; anything more competes with delivery hours.

---

**Related:** ROADMAP.md (phases/gates) · Companion Analysis §3 (schema + pipeline rationale) ·
ADR-004 (data sourcing) · ADR-005 (compliance boundary) · RISKS.md#data-tos, #dpdp, #bus-factor.
