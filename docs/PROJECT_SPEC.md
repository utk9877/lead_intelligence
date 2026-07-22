# Project Spec — AI Lead Intelligence Platform

> **Status:** Phase 0 living document. Reflects the co-founder interview and market-research
> round one. Decisions ADR-001 through ADR-005 are all **accepted** (founder approval
> 2026-07-16) and shape the scope below. Economics are **placeholders flagged for
> validation**, not commitments.

## 1. Vision

Give any B2B seller targeting the Indian market a steady flow of **warm, researched, scored
accounts** — each one delivered with an evidence-cited case for *why this account* and *why
now*. We replace "here's a database, go dig" with "here are the accounts worth your next call,
and here's the proof."

## 2. Who we serve (ICP)

- **Buyer:** B2B SaaS startups and other B2B vendors **selling into India** (ADR-001).
- **Their pain:** incumbent tools (Apollo/ZoomInfo/Clay/Common Room) are US-first and weak on
  India and sub-200-employee companies; the India-native option (Pintel) sells a database of
  rows and signals that the buyer still has to interpret and work (COMPETITOR_ANALYSIS.md).
- **Job to be done:** "Tell me which Indian companies to go after this month, with a
  believable reason, so my small team spends its selling time on accounts that are actually in
  a buying window."

## 3. Positioning — "delivered intelligence"

We do **not** sell a database or a signals dashboard. We sell **delivered intelligence**:

- **Evidence-cited warm accounts.** Every "why this account / why now" claim links to its
  source — a filing, a job post, a news item, site content.
- **Deep-fit reasoning per account**, not filterable rows. The unit is *a researched account
  with a narrative*, not *a row you filter*.
- **Zero learning curve.** Because we deliver the outcome (ADR-002), the buyer skips the
  learning curve and "dashboard fatigue" that are incumbents' most-repeated complaints.

Contrast with the direct competitor: **Pintel sells a database + signals platform; we sell the
worked conclusion.** (COMPETITOR_ANALYSIS.md §6, §"Where We Win".)

## 4. Warm-signal definitions {#warm-signals}

Per ADR-003 (**proposed**), Phase 1 ships two signal types, both buildable now from public
data + LLMs:

**A. Buying-trigger events** — a company enters a buying window when we detect:

| Trigger | Public source (illustrative) |
|---------|------------------------------|
| Funding round | news, funding databases |
| Hiring surge / role signals | job posts, careers pages |
| New incorporation | MCA registry (CIN) |
| GST registration | GST data |
| Expansion (new office/entity) | filings, news, site content |
| Tech adoption | site tech-detection, job-post stack mentions |

**B. Deep-fit reasoning** — agentic per-account research that produces the evidence-cited
"why this account, why now," tying the triggers above to the specific seller's offering.

**Deferred (ADR-003):** lookalikes (need customer CRM history) and third-party intent (licensed,
~no India coverage today). Deferral is explicit, tracked in QUESTIONS.md with revisit triggers.

## 5. Service packaging *(placeholder economics — flagged for validation)*

> ⚠️ **All numbers below are placeholders to be validated in P0/P1 (see ASSUMPTIONS.md,
> QUESTIONS.md#pricing). Do not treat as pricing.**

Productized service (ADR-002): "**N** researched, scored, warm accounts per month in your
niche," delivered behind a human QA gate.

| Tier | Shape (placeholder) | Notes |
|------|--------------------|-------|
| Starter | ~N accounts/month, monthly retainer | Prove the motion |
| Growth | larger N, retainer + per-account | Primary tier |
| Per-account | ₹/researched-account | For spiky demand |

Both a **monthly retainer** and a **₹/account** unit are on the table; which one buyers prefer
is an open pricing question (QUESTIONS.md#pricing). Margin depends on **LLM + API cost per
researched account** (RISKS.md#llm-cost, ADR-004) — tracked as a first-class metric below.

## 6. Success metrics

- **Precision of "warm" calls** — of the accounts we call warm, what fraction the customer
  agrees are worth pursuing. This is the core quality metric.
- **Meetings booked per 100 delivered accounts** — the outcome the buyer actually pays for.
- **Cost per researched account** (LLM + registry API) — the unit economic that decides
  whether the service margin and the eventual platform hold up (ADR-004).
- **Delivery capacity** — accounts/month a duo can deliver at quality with agent leverage
  (ASSUMPTIONS.md#delivery-capacity).

---

## 7. Niche recommendation *(analysis — final pick deferred to founder validation calls)*

The niche is **undecided** (interview decision #5). Below is a data-driven shortlist; the
recommendation is analysis only — the **final pick needs the founder's validation calls, not
just this scoring.** Candidates are scored on three axes, each 1–5:

- **Signal richness** — how many strong, public buying triggers this segment emits.
- **Incumbent weakness** — how badly Apollo/ZoomInfo/Clay/Pintel serve sellers into it.
- **Buyer reachability** — how easily we can find and close the *sellers* who target it.

| Candidate niche (the seller targets…) | Signal richness | Incumbent weakness | Buyer reachability | Score |
|---|---|---|---|---|
| **D2C / e-commerce brands** | 5 — rich site tech-detect, marketplace/IndiaMART presence, ad activity, funding | 4 — long tail of small brands incumbents miss | 4 — sellers (agencies, SaaS) are concentrated and reachable | **13** |
| **Manufacturers / exporters** | 4 — GST slabs, trade/export data, tender activity, incorporation | 5 — deeply underserved by US-first tools | 3 — seller pool more fragmented | **12** |
| **Funded / scaling SMBs** | 5 — hiring + funding + incorporation triggers stack cleanly | 4 — sub-200-employee blind spot | 4 — VC/ecosystem channels make sellers reachable | **13** |

**Read of the table:** D2C/e-commerce and funded/scaling SMBs tie on richest signals +
reachable buyers; manufacturers/exporters score highest on incumbent weakness but are harder
to reach on the *seller* side. A reasonable opening bet is **funded/scaling SMBs** (cleanest
trigger stack, ecosystem channels to find sellers) **or D2C/e-commerce** (richest public data
footprint). **This is a recommendation to test, not a decision** — it goes to
QUESTIONS.md#niche for founder validation calls before it becomes an ADR.

---

## Related documents

- Decisions: `ADR/` (ADR-001…005)
- Competitive detail: `COMPETITOR_ANALYSIS.md`
- What must be true: `ASSUMPTIONS.md`
- What could go wrong: `RISKS.md`
- Open decisions: `QUESTIONS.md`
- Phased build & gates: `ROADMAP.md`
