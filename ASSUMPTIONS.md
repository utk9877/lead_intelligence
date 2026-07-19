# Assumptions

Each assumption is something that **must be true** for the plan to hold, paired with **how we
will validate it**. An assumption that fails should trigger a revisit of the ADR(s) it
supports. Ordered roughly by how load-bearing it is.

---

### A1. Enough into-India B2B sellers with budget exist {#market-demand}

**Statement:** There is a large-enough population of B2B sellers targeting the Indian market
who feel the "which Indian accounts, why now" pain and have budget to pay for a delivered
service.
**Supports:** ADR-001, ADR-002.
**Validation:** P0 — 15–20 discovery calls with candidate buyers in the shortlisted niches;
count how many name this pain unprompted and quote a budget. Gate to P1: ≥3 willing to pay for
a pilot.

### A2. Company-level intel is sellable without person-level contacts on day one {#company-level-sellable}

**Statement:** Buyers will pay for warm, evidence-cited *company-level* accounts even before we
supply person-level contact data ourselves (ADR-005), because they can bridge the last mile.
**Supports:** ADR-003, ADR-005.
**Validation:** In discovery calls, explicitly test the company-level-only offer. If buyers say
"useless without contacts," the assumption fails → escalate the contact-partner decision
(QUESTIONS.md#contact-data) before P1.

### A3. MCA/GST API costs stay bootstrap-viable at delivery volume {#api-cost}

**Statement:** Pay-per-call registry/verification APIs (Attestr/Surepass/Karza/Signzy class)
remain cheap enough that cost-per-researched-account leaves a workable margin as volume grows.
**Supports:** ADR-004.
**Validation:** P0 — obtain real per-call pricing from ≥2 vendors; model cost-per-account at
target N. Recompute whenever pricing or volume changes. Tie to PROJECT_SPEC.md cost-per-account
metric.
**Early signal (research round two, 2026-07-19):** supportive — Attestr publicly documents
MCA/CIN and GSTIN endpoints, and indicative marketplace pricing (~₹10–100 per business check,
Signzy class) fits the envelope. **Caveat to test in the vendor comparison:** some vendors
carry enterprise platform minimums (~₹2–15 lakh/yr) — quotes must confirm true pay-per-call
tiers with no platform commit, or this assumption weakens.

### A4. A duo can deliver N accounts/month/customer with agent leverage {#delivery-capacity}

**Statement:** With scripts + agents behind a human QA gate, a solo/duo team can deliver the
promised N researched accounts per customer per month at acceptable quality.
**Supports:** ADR-002, ROADMAP P1.
**Validation:** P1 — time-and-motion on the first real deliveries; measure human-minutes per
researched account and the QA reject rate. If capacity < promised N at quality, adjust N,
pricing, or agent tooling before scaling customers. Related risk: RISKS.md#bus-factor,
RISKS.md#llm-cost.

### A5. Public-data triggers + deep-fit reasoning are a strong-enough signal {#signal-strength}

**Statement:** Buying triggers (funding/hiring/incorporation/GST/expansion/tech) plus agentic
deep-fit reasoning predict "warm" well enough that our precision metric satisfies buyers —
without lookalikes or intent data.
**Supports:** ADR-003.
**Validation:** P1 — track precision-of-"warm" (PROJECT_SPEC.md metric) against customer
feedback on delivered accounts. If precision is weak, revisit ADR-003's deferral of
lookalikes/intent.

### A6. Registry anchoring gives clean entity resolution in practice {#entity-resolution}

**Statement:** CIN/GSTIN anchoring actually yields clean, low-duplicate entity resolution for
the companies our niches care about.
**Supports:** ADR-001.
**Validation:** P1 — measure duplicate/mismatch rate on a real batch; specifically test the
edge cases in QUESTIONS.md (unregistered businesses, proprietorships without CIN). If edge
cases dominate a niche, factor that into the niche decision.
