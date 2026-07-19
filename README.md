# AI Lead Intelligence Platform — Living Docs

Design scaffold for an **AI Lead Intelligence Platform**: warm, researched, evidence-cited
Indian-company accounts, delivered to B2B sellers targeting the Indian market. We are in
**Phase 0 — design, not build**: these are working documents that every subsequent iteration
reads from and edits. No code or infrastructure yet; architecture lives here as *design
content* only.

## The documents

| Document | Purpose |
|----------|---------|
| [`PROJECT_SPEC.md`](PROJECT_SPEC.md) | Vision, ICP, "delivered intelligence" positioning, warm-signal defs, packaging (placeholder economics), success metrics, and the **niche recommendation** |
| [`COMPETITOR_ANALYSIS.md`](COMPETITOR_ANALYSIS.md) | Teardowns (Clay, Common Room, Apollo, ZoomInfo, PDL, **Pintel**, Slintel/6sense, Draup, Tofler/ZaubaCorp) + "where we win" |
| [`ASSUMPTIONS.md`](ASSUMPTIONS.md) | What must be true, each with a validation method |
| [`RISKS.md`](RISKS.md) | Prioritized risks, each with a mitigation |
| [`QUESTIONS.md`](QUESTIONS.md) | Every open decision, so nothing is dropped |
| [`ROADMAP.md`](ROADMAP.md) | P0→P3 with revenue + learning gates |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Implementation blueprint: services, monorepo tree, Docker/Kubernetes design, AWS hosting path (design content — nothing built) |
| [`ADR/`](ADR/) | Architecture Decision Records — the decision spine |

## Reading order

1. **`PROJECT_SPEC.md`** — what we're building and for whom.
2. **`COMPETITOR_ANALYSIS.md`** — why it's defensible.
3. **`ADR/`** — the decisions everything else cites.
4. **`ASSUMPTIONS.md`** → **`RISKS.md`** — what must hold, what could break it.
5. **`QUESTIONS.md`** — what's still open.
6. **`ROADMAP.md`** — how it gets built, and the gates.

## Decision status (ADRs)

| ADR | Decision | Status |
|-----|----------|--------|
| [001](ADR/ADR-001-india-market-leads.md) | Indian-company leads; into-India B2B sellers as customers | ✅ **accepted** |
| [002](ADR/ADR-002-service-before-platform.md) | Productized service before self-serve platform | ✅ **accepted** |
| [003](ADR/ADR-003-signal-phasing.md) | Signal phasing — triggers + deep-fit first; intent/lookalikes deferred | ✅ **accepted** |
| [004](ADR/ADR-004-payper-call-data-apis.md) | Data via pay-per-call registry APIs + own compliant crawling | ✅ **accepted** |
| [005](ADR/ADR-005-company-level-first.md) | Company-level intelligence first; contacts via compliant partners | ✅ **accepted** |

> All five ADRs are now **accepted** (founder approval 2026-07-16). ADR-003 was accepted with
> the note that it diverges from the original "all four signals" preference — the deferral of
> lookalikes/intent is tracked in QUESTIONS.md#deferred-signals with revisit triggers.
> [`ADR/ADR-000-template.md`](ADR/ADR-000-template.md) is the template for new records.

## Conventions

- Cross-references use the form `FILE.md#anchor` (e.g. `RISKS.md#dpdp`).
- Economics and figures marked as **placeholders** are for validation, not commitments.
- Sourcing: research is transcribed as authoritative; unverified claims carry
  `[source: internal research — verify]` — never a fabricated URL.
