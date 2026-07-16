# Open Questions

Every open decision raised in the co-founder interview and in the Phase-0 plan lives here, so
nothing is silently dropped. Each has an **owner path** (how it gets resolved) and, where
relevant, the ADR/assumption it will feed. Nothing here is decided.

---

### Q1. Niche pick — validate the shortlist {#niche}

Interview decision #5 is undecided. PROJECT_SPEC.md §7 scores three candidates (D2C/e-commerce,
manufacturers/exporters, funded/scaling SMBs) but the pick is **deferred to founder validation
calls**, not settled by scoring.
**Resolve via:** discovery calls (ASSUMPTIONS.md#market-demand). Outcome becomes a new ADR.

### Q2. Pricing model — retainer vs ₹/account vs hybrid {#pricing}

PROJECT_SPEC.md §5 lists both; economics are placeholders.
**Resolve via:** pricing questions in discovery; model against measured cost-per-account
(ASSUMPTIONS.md#api-cost). Feeds a pricing ADR.

### Q3. Contact-data strategy — build vs partner {#contact-data}

ADR-005 defers person-level contacts to compliant partners, but *which* partner, at what cost,
and whether buyers need contacts at all in P1 is open.
**Resolve via:** test company-level-only offer (ASSUMPTIONS.md#company-level-sellable); if
contacts are required, evaluate compliant providers. Feeds a follow-on to ADR-005.

### Q4. Founder distribution / network advantages {#distribution}

What existing network, audience, or channel does the founder have to reach the *sellers* in the
chosen niche? This materially affects Q1 (buyer-reachability axis) and go-to-market speed.
**Resolve via:** founder self-audit + factor into niche scoring.

### Q5. Entity-resolution edge cases {#entity-resolution}

How do we handle **unregistered businesses** and **proprietorships without a CIN**? These fall
outside the registry-anchored graph (ADR-001) and could dominate some niches.
**Resolve via:** measure edge-case rate per niche (ASSUMPTIONS.md#entity-resolution); may
constrain niche choice or require a secondary identifier (e.g. GSTIN-only, IndiaMART presence).

### Q6. Deferred signals — revisit triggers {#deferred-signals}

ADR-003 defers **lookalikes** (need customer CRM history) and **third-party intent** (licensed,
~no India coverage). When do we revisit?
**Revisit trigger:** lookalikes — once ≥1 customer shares CRM/win history; intent — once a
viable India intent source or coverage exists. Tracked, not dropped.

### Q7. Registry API vendor selection {#api-vendor}

Which pay-per-call vendor(s) — Attestr / Surepass / Karza / Signzy class (ADR-004) — on price,
coverage, and reliability?
**Resolve via:** P0 pricing/coverage comparison (ASSUMPTIONS.md#api-cost). Feeds ADR-004
detail.

### Q8. ADRs 003–005 approval {#adr-approval} — ✅ RESOLVED

ADR-003 (signal phasing), ADR-004 (pay-per-call data), ADR-005 (company-level first) were
**accepted** by founder approval on 2026-07-16. ADR-003 was accepted with the noted divergence
from the original "all four signals" preference; the deferral of lookalikes/intent remains
tracked in Q6. No open action.

### Q9. Target N — accounts per customer per month {#target-n}

The "N researched accounts/month" promise (PROJECT_SPEC.md §5) has no committed value.
**Resolve via:** delivery capacity measurement (ASSUMPTIONS.md#delivery-capacity) in P1 sets a
sustainable N.
