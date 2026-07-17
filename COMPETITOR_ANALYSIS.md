# Competitor Analysis

> **Sourcing note.** This document transcribes market-research round one as authoritative.
> Where a figure or claim has a trivially-known public source, a URL is given. Everything
> else is marked `[source: internal research — verify]` and should be confirmed before it is
> used in external-facing material (a sales deck, an investor memo). No figure below has been
> invented; unverified ones are flagged, not dressed up.

Competitors fall into three layers, and we sit across all three deliberately:

- **GTM-engineering / signal platforms** — Clay, Common Room.
- **Contact/company databases** — Apollo, ZoomInfo, PDL.
- **India data layer** — Pintel.ai (direct), Slintel/6sense, Draup, Tofler/ZaubaCorp.

---

## 1. Clay — GTM-engineering platform *(indirect, category-defining)*

- **What it is:** A GTM-engineering platform with agentic research ("Claygent") that
  enriches and researches accounts/people by chaining data providers and LLM steps.
- **Business model:** Credit-based usage on top of tiered seats; reportedly ~$100M ARR.
  `[source: internal research — verify]`
- **Architecture (as understood):** Spreadsheet-like tables → waterfall enrichment across
  many third-party providers → LLM/agent steps (Claygent) for research → export/sync.
- **Strengths:** Enormously flexible; strong agentic research; large integration catalog;
  category mindshare.
- **Weaknesses:** Expensive credit burn; a **2–4 week learning curve**; needs a RevOps/GTM-
  engineer skillset to operate; **US-centric data** — weak on India and small companies.
  `[source: internal research — verify]`
- **Where we differ:** Clay sells *capability you operate*; we sell *the finished outcome*.
  Their learning curve is our wedge (ADR-002).

## 2. Common Room — signal aggregation *(indirect)*

- **What it is:** Aggregates "signals" (community, product, web, social) into a person/account
  view for GTM teams.
- **Business model:** Subscription; entry around **$625+/mo**. `[source: internal research — verify]`
- **Strengths:** Broad signal capture; good for community-led/PLG motions.
- **Weaknesses:** **"Dashboard fatigue"** — surfaces signals but doesn't tell you *what to do*;
  poor fit where prospects aren't active in online communities, i.e. **most Indian SMBs**.
  `[source: internal research — verify]`
- **Where we differ:** We deliver a decision ("go after this account, here's why now"), not a
  dashboard of raw signals.

## 3. Apollo — contact/company database *(indirect)*

- **What it is:** Sales-intelligence database + sequencing/engagement.
- **Business model:** Freemium → per-seat tiers with credit limits.
- **Strengths:** Large global contact database; low entry price; all-in-one prospecting.
- **Weaknesses:** Systematically weak on **India** and on **sub-200-employee companies**;
  contact **decay ~22%/yr**. `[source: internal research — verify]`
- **Where we differ:** India-first, registry-anchored, freshness from live triggers rather
  than a decaying static database.

## 4. ZoomInfo — enterprise data platform *(indirect)*

- **What it is:** Enterprise B2B data + intelligence platform.
- **Business model:** High-ACV annual enterprise licenses.
- **Strengths:** Deep US/global coverage; mature intent + org data.
- **Weaknesses:** Same India + SMB gap as Apollo; expensive; not bootstrap-relevant as a
  *supplier* to us (ADR-004 rules out enterprise licenses). `[source: internal research — verify]`
- **Where we differ:** We don't compete on breadth of a static US database; we compete on
  India depth + delivered reasoning.

## 5. People Data Labs (PDL) — data-as-infrastructure *(supplier-adjacent)*

- **What it is:** Person/company datasets sold via API for others to build on.
- **Business model:** API/data licensing.
- **Relevance:** A potential *ingredient* supplier, but US-centric; India coverage is the
  question. Weak fit for our registry-anchored India graph. `[source: internal research — verify]`
- **Where we differ:** Our data spine is CIN/GSTIN registry data (ADR-001/004), which PDL
  does not anchor on.

## 6. Pintel.ai — **DIRECT COMPETITOR (deepest teardown)**

- **What it is:** Bengaluru-based India B2B data/signals platform. Founded ~2023; ~$1M raised.
  `[source: internal research — verify]`
- **Product:** Claims a **100M+ company India database**, built on **MCA / IndiaMART /
  trade-directory** data, with **buying signals** and **verified contacts**.
  `[source: internal research — verify]`
- **Business model (as understood):** Sells a **database + signals platform** (self-serve /
  seat + data access), i.e. the "here are filterable rows and signals, you go work them" shape.
- **Strengths:** India-first like us; already has scaled registry/trade data; validates the
  thesis that India B2B data is a real market; verified-contact story we deliberately defer
  (ADR-005).
- **Weaknesses / opening for us:** They sell a **platform of rows and signals** — which means
  they inherit exactly the incumbent complaints (learning curve, "what do I *do* with this?").
  They optimize for *breadth of data*, not *per-account delivered reasoning*.
- **Significance:** Both **validation** (someone raised money doing India B2B data) **and
  threat** (a funded, on-thesis competitor). Tracked in RISKS.md#competitor-encroachment.
- **Where we win:** See §"Where We Win" — delivered, evidence-cited intelligence vs a
  self-serve database.

## 7. Slintel / 6sense — intent data + exit proof *(indirect / strategic)*

- **What it is:** Slintel, an Indian-founded intent-data player, was **acquired by 6sense
  (2021)**. `[source: internal research — verify]`
- **Relevance:** Two things — (a) intent data as a category (which we *defer*, ADR-003, given
  weak India coverage today), and (b) **proof of an exit path** for an Indian-founded
  GTM-data company.
- **Where we differ:** We don't lead with licensed intent; we lead with public-data triggers
  + deep-fit reasoning.

## 8. Draup — talent/account intelligence *(indirect)*

- **What it is:** Account and talent intelligence, more enterprise/analyst-oriented.
- **Relevance:** Adjacent "intelligence" positioning; different buyer (enterprise strategy/
  talent) and price point. `[source: internal research — verify]`
- **Where we differ:** SMB/startup GTM buyer, delivered-service motion, India-registry spine.

## 9. Tofler / ZaubaCorp — India company data layer *(data source & baseline)*

- **What they are:** Consumer/SMB-facing portals surfacing **MCA registry data** (financials,
  directors, filings) per company. `[source: internal research — verify]`
- **Relevance:** They prove registry data is *accessible and productizable* in India; they are
  a **baseline/reference layer**, not a GTM competitor — no signals, no scoring, no delivery.
- **Where we differ:** We turn registry data into *warm, scored, evidence-cited accounts for a
  specific seller's niche*, not a per-company lookup page.

---

## Where We Win

Our differentiation is one sentence: **we sell delivered intelligence, not a database.**

| Incumbent complaint | Our answer |
|---------------------|------------|
| Clay/Common Room learning curve & "dashboard fatigue" | **Zero learning curve** — we deliver finished, scored accounts (ADR-002) |
| Apollo/ZoomInfo India + SMB blind spot & 22%/yr decay | **India-first, registry-anchored (CIN/GSTIN), freshness from live triggers** (ADR-001) |
| Pintel sells filterable rows + signals | **Per-account deep-fit reasoning** — "why this account, why now," every claim linked to its source (filing, job post, news, site content) |
| Intent data has no India coverage | We **defer** intent (ADR-003) and win on public-data triggers + agentic reasoning instead |

**The structural edge incumbents can't cheaply copy:** India's universal company identifiers
(CIN, GSTIN) let us build a **registry-anchored company graph with clean entity resolution**.
No US-first player is architected for this. That is the moat (ADR-001).

**The wedge is the outcome, not the tool:** the two biggest, most-repeated incumbent
complaints — learning curve and "signals without a decision" — are *eliminated* by delivering
the decision instead of the toolkit.
