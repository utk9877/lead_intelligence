# ADR-003: Signal phasing — buying triggers + deep-fit reasoning first; intent & lookalikes deferred

- **Status:** proposed *(awaiting founder approval — user originally wanted all four signal types)*
- **Date:** 2026-07-16
- **Deciders:** Founders (solo/duo)
- **Related:** ADR-002; PROJECT_SPEC.md#warm-signals; ASSUMPTIONS.md#company-level-sellable; RISKS.md#intent-coverage

## Context

Four candidate signal types were on the table: (1) buying-trigger events, (2) deep-fit
reasoning, (3) lookalikes, (4) third-party intent data. The founder originally wanted all
four. But two of them are not buildable cheaply *today*:

- **Lookalikes** require a customer's own CRM/win history to model against — we won't have
  that until we have paying customers with data to share.
- **Third-party intent data** is licensed, expensive, and has effectively no India coverage
  today (the incumbent intent vendors are US-centric — see COMPETITOR_ANALYSIS.md). Buying
  it now would break the bootstrap constraint (ADR-004) for near-zero India signal.

The other two are buildable immediately from public data + LLMs and are exactly the
"delivered intelligence" we differentiate on.

## Decision

We will ship, in **Phase 1**, two signal types only:

1. **Buying-trigger events** — funding rounds, hiring surges, new incorporation, GST
   registration, expansion (new offices/entities), and tech adoption.
2. **Deep-fit reasoning** — agentic per-account research producing an evidence-cited
   "why this account, why now."

We will **defer** lookalikes (revisit once customers share CRM history) and intent data
(revisit when India coverage or a viable data source exists). Deferral is explicit, not a
silent drop — both live in QUESTIONS.md with a revisit trigger.

## Options considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Triggers + deep-fit first (chosen) | Buildable now from public data + LLMs; *is* the differentiation | Two signal types, not four, at launch | ✅ chosen |
| All four at launch | Matches original ask | Lookalikes need CRM we lack; intent is licensed + no India coverage; breaks bootstrap | rejected — deferred |
| Triggers only | Cheapest | Loses the deep-fit "delivered intelligence" edge | rejected |

## Consequences

- **Positive:** launch scope is fully buildable on public data + LLMs; focuses effort on the
  differentiator (deep-fit, evidence-cited) rather than commodity intent rows.
- **Negative / cost:** no lookalike/intent story in early sales conversations — must be framed
  as roadmap, not gap.
- **Follow-on:** creates ASSUMPTIONS.md#company-level-sellable (that triggers + deep-fit are
  enough to sell) and RISKS.md#intent-coverage.

## Status history

- 2026-07-16 — proposed
