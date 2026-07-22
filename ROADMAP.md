# Roadmap

Phased so that **revenue and learning gates** — not calendar dates — decide when we advance.
Architecture appears here as *design content only* (per Phase-0 scope: no code, no infra yet);
trade-offs are surfaced before anything is locked.

```
P0 ──▶ P1 ──▶ P2 ──▶ P3
docs  manual  productized  self-serve
+niche +agent  pipeline    platform
```

---

## P0 — Discovery & living docs *(current phase)*

**Goal:** Establish the design scaffold and choose a niche to bet on.
**Work:** These living documents; 15–20 buyer discovery calls; registry-API pricing/coverage
comparison; niche validation (PROJECT_SPEC.md §7, QUESTIONS.md#niche); the single-design-partner
concept proof below, as soon as one committed buyer exists.

**Concept proof — single design partner {#design-partner}:** the moment the calls produce one
committed buyer (paying, or a formally committed pilot), run the entire loop end-to-end for
that one customer, in the niche *they* demand: manual scripts + agents, human QA on every
account, delivery via Slack/email. No pipeline is built for this — it is the P1 shape at
n = 1. Purpose: prove the concept end-to-end and convert two gate items from models into
measurements — real cost-per-researched-account (ASSUMPTIONS.md#api-cost) and whether
company-level-only accounts are sellable (ASSUMPTIONS.md#company-level-sellable). One design
partner does **not** settle the niche pick by itself (QUESTIONS.md#niche — single-customer
overfit risk); discovery calls continue in parallel.

**Learning gate → P1:** a chosen niche backed by real calls; ≥3 buyers willing to pay for a
pilot (ASSUMPTIONS.md#market-demand); an end-to-end concept proof — ≥1 batch of warm,
evidence-cited accounts delivered to the design partner with cost-per-account measured, not
modelled (ASSUMPTIONS.md#api-cost); founder-approved ADR-003/004/005
(QUESTIONS.md#adr-approval).
**Revenue gate:** none (pre-revenue; design-partner payment welcome but not required to exit P0).

## P1 — Manual service with agent leverage

**Goal:** Deliver the promised outcome by hand, behind a human QA gate, and learn what "warm"
means for real buyers.
**Shape:** The "engine" is **scripts + agents behind a human QA gate** — not a product. A
person reviews and signs off every delivered account (ADR-002).
**Work:** Onboard 3–5 paying pilot customers in the chosen niche; deliver N researched,
scored, evidence-cited accounts/month; measure precision-of-"warm," meetings booked per 100
accounts, human-minutes/account, and cost/account (PROJECT_SPEC.md §6).
**Learning gate → P2:** precision-of-"warm" acceptable to customers
(ASSUMPTIONS.md#signal-strength); delivery capacity understood (ASSUMPTIONS.md#delivery-
capacity); repeatable, documented delivery runbook.
**Revenue gate → P2:** 3–5 paying customers retained; unit economics (cost/account vs price)
positive or clearly improvable.

## P2 — Productized pipeline

**Goal:** Turn the manual runbook into a repeatable internal pipeline — still delivered as a
service, but the humans do QA and edge-handling, not the rote work.

**Design (content only — to be elaborated with trade-offs before locking):**

```
source adapters ──▶ registry-anchored company graph ──▶ agent research/scoring ──▶ delivery
(MCA/GST APIs,       (Postgres + pgvector,               (deep-fit reasoning,       (Slack / CRM)
 job posts, news,     CIN/GSTIN entity resolution)        evidence citations)
 site content)
```

**Work:** Build source adapters (ADR-004); a **Postgres + pgvector** registry-anchored company
graph keyed on CIN/GSTIN (ADR-001); the agent research/scoring layer (ADR-003 signals); and
Slack/CRM delivery. Keep the human QA gate.
**Learning gate → P3:** pipeline reduces human-minutes/account materially at held-or-better
precision; entity-resolution edge cases (QUESTIONS.md#entity-resolution) handled.
**Revenue gate → P3:** service margin healthy at meaningfully higher customer count; demand
signal for self-serve.

## P3 — Self-serve platform

**Goal:** Expose the engine as a product customers operate themselves — *after* the service has
taught us scoring, packaging, and buyer.
**Work:** Self-serve onboarding, niche configuration, delivery UX; contact-data partner
integration if validated (ADR-005, QUESTIONS.md#contact-data); revisit deferred signals —
lookalikes / intent (ADR-003, QUESTIONS.md#deferred-signals) — as data allows.
**Gates:** entered only on P2 economics + clear self-serve demand; not a default endpoint.

---

**Gate discipline:** we do not advance a phase because time passed — only when its learning
*and* revenue gates are met. Each gate review also re-checks RISKS.md.
