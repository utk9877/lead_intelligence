# Risks

Prioritized. Each risk: what it is, why it matters, and the current **mitigation**. Reviewed
every phase gate (ROADMAP.md).

---

### R1. DPDP / scraping legal ambiguity — **top legal risk** {#dpdp}

**What:** The DPDP Act 2023 §3(c)(ii) exempts *publicly-available* personal data, but
government statements (Rajya Sabha, **Aug 2024**) indicate that *scraping* such data can still
trigger IT Act + DPDP obligations. The position is genuinely ambiguous.
`[source: internal research — verify exact citation before external use]`
**Why it matters:** Our whole data motion depends on collecting public data; a hostile
interpretation could restrict it.
**Mitigation:** Company-level intelligence first — company facts (CIN/GSTIN/filings/funding)
are not personal data (ADR-005). Any person-level contact data comes only from compliant
third-party providers, never our own person scraping (ADR-005). Track regulatory movement each
phase gate; keep the ADR-005 boundary bright.

### R2. Competitor encroachment — Pintel or Clay moving down-market into India {#competitor-encroachment}

**What:** Pintel (funded, on-thesis, Bengaluru) could add delivered-reasoning; Clay/Common
Room/Apollo could invest in India + SMB coverage.
**Why it matters:** Erodes the two things we win on (India depth, delivered reasoning).
**Mitigation:** Move fast on the *delivery* motion (learning-curve moat is behavioral, not just
data); deepen the registry-anchored graph (ADR-001) that US-first players aren't architected
for; win reference customers in a focused niche before a bigger player notices it.

### R3. Small-wallet ICP churn {#small-wallet}

**What:** B2B sellers into India, especially those targeting SMBs, may have small budgets and
churn quickly.
**Why it matters:** Threatens retention and unit economics of a service business.
**Mitigation:** Niche selection weights *buyer reachability & willingness to pay*
(PROJECT_SPEC.md §7); validate budget in discovery (ASSUMPTIONS.md#market-demand); price on
delivered outcome (meetings booked) so value is legible; keep delivery cost low via agent
leverage.

### R4. Founder-pair bus factor {#bus-factor}

**What:** Solo/duo team; delivery capacity and all knowledge sit in 1–2 people.
**Why it matters:** Illness, churn, or overload stalls delivery and the company.
**Mitigation:** Productize the engine early (scripts + agents behind QA) so the *process*,
not a person, does the work (ADR-002, ROADMAP P1→P2); document runbooks; cap concurrent
customers to sustainable capacity (ASSUMPTIONS.md#delivery-capacity).

### R5. LLM + API cost per researched account {#llm-cost}

**What:** Deep-fit agentic research plus per-call registry APIs cost real money per account.
**Why it matters:** If cost-per-account is too high, both service margin and the eventual
self-serve platform break.
**Mitigation:** Track cost-per-account as a first-class metric (PROJECT_SPEC.md §6); model it
in P0 (ASSUMPTIONS.md#api-cost); tune agent depth and caching; set N and pricing against
measured cost.

### R6. Data-source Terms-of-Service traps {#data-tos}

**What:** Scraping LinkedIn / Naukri and similar sites is the classic ToS trap — and squarely
person-level, compounding R1.
**Why it matters:** ToS violations and person-level scraping create legal and platform-ban
exposure.
**Mitigation:** Do **not** scrape LinkedIn/Naukri for person data. Prefer alternatives:
registry APIs (ADR-004), company career pages / job boards at the *posting* level (a hiring
*signal*, not a person record), news, and company sites. Person-level contact data via
compliant partners only (ADR-005). Maintain an allowed-sources list and review it each gate.
