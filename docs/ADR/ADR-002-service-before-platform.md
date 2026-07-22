# ADR-002: Productized service before self-serve platform

- **Status:** accepted
- **Date:** 2026-07-16 (locked in co-founder interview)
- **Deciders:** Founders (solo/duo)
- **Related:** ADR-001; ADR-003; ROADMAP.md; ASSUMPTIONS.md#delivery-capacity

## Context

We are solo/duo and bootstrapped (ADR context: no big-data licenses, revenue-funded). Two
go-to-market shapes are possible: build a self-serve SaaS product first, or sell a
productized service that a small team delivers by hand (with heavy agent leverage) and
productize the engine underneath over time. Building a platform first burns runway before
we've learned what "warm" actually means for our buyers; incumbents' biggest complaints are
learning-curve and "dashboard fatigue" (COMPETITOR_ANALYSIS.md) — problems a *delivered*
outcome sidesteps entirely.

## Decision

We will lead with a **productized service** — "*N* researched, scored, warm accounts per
month in your niche" — delivered behind a human QA gate, and turn the engine into a
self-serve product only after the service has taught us the scoring, the packaging, and the
buyer. The service is the way we learn; the platform is the way we scale.

## Options considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Productized service first (chosen) | Revenue early; learn scoring/ICP from real delivery; zero buyer learning-curve | Manual effort per customer; capacity-bound | ✅ chosen |
| Self-serve platform first | Scales without headcount | Long build before revenue; guesses at "warm"; burns runway | rejected |
| Pure consulting | Fastest cash | No productizable engine, no moat | rejected |

## Consequences

- **Positive:** revenue funds the build; every delivery is a labelled data point for the
  scoring model; differentiates on outcome, not dashboard.
- **Negative / cost:** delivery capacity is the constraint (ASSUMPTIONS.md#delivery-capacity,
  RISKS.md#bus-factor); margins depend on agent leverage and LLM cost per account
  (RISKS.md#llm-cost).
- **Follow-on:** shapes ROADMAP P1→P3; makes ADR-003 (signal phasing) a delivery-scoping
  decision, not just a technical one.

## Status history

- 2026-07-16 — accepted (co-founder interview)
