# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **Phase-0 living-documents scaffold** for "Lead Intelligence" — a planned AI lead-intelligence
platform delivering warm, researched, evidence-cited *Indian company* accounts to B2B sellers
targeting India.

**There is no code, no build, no tests, and no infrastructure.** There are no build/lint/test
commands to run. The repository contains Markdown design documents only. Architecture exists here
as *design content*, not implementation. Do not scaffold code, add tooling, or create a package
manifest unless explicitly asked — Phase 0 is deliberately design-only (see `ROADMAP.md`).

## Architecture: a cross-linked document graph

The "system" is the documents and the links between them. Each file owns one concern, and the
others cite it rather than restating it. Changing one document usually obliges you to update the
documents that reference it.

| File | Owns |
|---|---|
| `PROJECT_SPEC.md` | Vision, ICP, "delivered intelligence" positioning, warm-signal definitions, packaging, success metrics, niche shortlist (§7) |
| `COMPETITOR_ANALYSIS.md` | Competitor teardowns (Clay, Common Room, Apollo, ZoomInfo, PDL, **Pintel.ai** = direct, Slintel/6sense, Draup, Tofler/ZaubaCorp) + "Where We Win" |
| `ADR/` | The decision spine — ADR-001…005, all **accepted** 2026-07-16. `ADR-000-template.md` is the template |
| `ASSUMPTIONS.md` | A1–A6: what must be true, each with a validation method |
| `RISKS.md` | R1–R6: each with a mitigation; re-checked at every phase gate |
| `QUESTIONS.md` | Q1–Q9 open decisions, so nothing is silently dropped |
| `ROADMAP.md` | P0→P3 phases, each with a **learning gate** and a **revenue gate** |
| `ARCHITECTURE.md` | Implementation blueprint (services, monorepo tree, Docker/K8s, AWS path) — still design content, phase-gated activation |

Reading order for orientation: `PROJECT_SPEC.md` → `COMPETITOR_ANALYSIS.md` → `ADR/` →
`ASSUMPTIONS.md` → `RISKS.md` → `QUESTIONS.md` → `ROADMAP.md`.

## The accepted decisions that constrain all work

These five ADRs are accepted and bound any proposal you make. Contradicting one requires a new
ADR, not an edit in passing.

- **ADR-001** — Indian companies as the leads; into-India B2B sellers as customers. The moat is
  registry anchoring on CIN/GSTIN (universal Indian company identifiers the US lacks).
- **ADR-002** — Productized service *before* self-serve platform. The service is how we learn what
  "warm" means; the platform is how we scale later.
- **ADR-003** — Ship two signal types only: buying triggers + deep-fit reasoning. **Lookalikes and
  third-party intent are deferred**, with revisit triggers in `QUESTIONS.md#deferred-signals`.
- **ADR-004** — Data via pay-per-call registry APIs (Attestr/Surepass/Karza/Signzy class) + own
  compliant crawling. **No enterprise data licenses** (bootstrap constraint).
- **ADR-005** — **Company-level intelligence only.** Person/contact data only from compliant
  third-party partners.

## Non-obvious conventions you must follow

**Sourcing discipline.** Unverified claims carry the literal marker
`[source: internal research — verify]`. **Never fabricate a URL or citation.** Only give a URL when
the source is trivially and genuinely known. This rule is load-bearing — much of
`COMPETITOR_ANALYSIS.md` and the DPDP legal position in `RISKS.md#dpdp` rests on unverified
research and is flagged as such.

**Economics are placeholders, never commitments.** All pricing, cost-per-account, margin, and the
"N accounts/month" figure are explicitly unvalidated (`PROJECT_SPEC.md` §5,
`QUESTIONS.md#pricing`). Anywhere they appear — especially in external-facing material — they must
be visibly marked as illustrative/pending validation.

**The compliance boundary is a hard line (ADR-005 + `RISKS.md#dpdp`, `#data-tos`).** Company-level
facts (CIN, GSTIN, filings, funding, org-level hiring) are not personal data. Do **not** propose
scraping LinkedIn, Naukri, or any person-level data. Job posts are used at the *posting* level as a
hiring signal, never as person records. The DPDP Act 2023 §3(c)(ii) public-data exemption is in
genuine tension with Aug-2024 government signalling that scraping public personal data may still
trigger obligations — that ambiguity is precisely why the company-level boundary exists.

**Cross-references use `FILE.md#anchor`** (e.g. `RISKS.md#dpdp`). Explicit anchors such as
`{#market-demand}`, `{#dpdp}`, `{#niche}` are link targets — renaming or removing one breaks
inbound links from other documents. Grep for an anchor before changing it.

**Keep status tables in sync.** ADR status appears in both the ADR file's front-matter *and* its
"Status history" section, *and* in the decision table in `README.md`. A status change means editing
all of them.

**Gate discipline (`ROADMAP.md`).** Phases advance only when *both* the learning and revenue gates
are met — never because time passed. Don't propose work that assumes a later phase has been
entered.

**Open questions stay open.** `QUESTIONS.md` items (notably the niche pick, Q1) are deliberately
undecided pending founder validation calls. Present analysis as a recommendation to test, not a
decision — the niche scoring in `PROJECT_SPEC.md` §7 explicitly is not a decision.

## Generated deliverables

One PDF sits in the repo root: `Lead_Intelligence_Companion_Analysis.pdf` (market research +
architecture + validation verdict, 2026-07-19). Three earlier stakeholder PDFs (Business Plan,
Execution Strategy, Software) were deliberately deleted on 2026-07-19 as stale snapshots — they
are regenerated from Markdown when the strategy stabilizes, not maintained. PDFs are produced
from self-contained styled HTML converted with headless Chrome, since this machine has no
pandoc/LaTeX/weasyprint:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="<output>.pdf" "<source>.html"
```

They are derived artifacts — the Markdown documents remain the source of truth. If strategy
changes, update the Markdown first, then regenerate.
