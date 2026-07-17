# ADR-001: Indian companies as the leads; into-India B2B sellers as first customers

- **Status:** accepted
- **Date:** 2026-07-16 (locked in co-founder interview)
- **Deciders:** Founders (solo/duo)
- **Related:** ADR-002; ADR-004; ADR-005; PROJECT_SPEC.md; RISKS.md#dpdp

## Context

We must choose *whose* companies we discover and *who* we sell that discovery to. The
incumbent data/GTM tools (Apollo, ZoomInfo, Clay, Common Room) are US-first and
systematically weak on India and on sub-200-employee companies (see
COMPETITOR_ANALYSIS.md). Two structural facts make India the strongest wedge:

1. **Universal company identifiers exist.** Every registered Indian company has a CIN
   (Corporate Identification Number) and most active businesses a GSTIN. The US has no
   equivalent universal registry key. A registry-anchored company graph with clean entity
   resolution is therefore a *structural* advantage no US-first player can easily copy.
2. **The registry data is cheaply accessible** via pay-per-call APIs (see ADR-004), so a
   bootstrapped team can build the data layer without an enterprise license.

## Decision

We will build lead intelligence about **Indian companies**, and sell it to **B2B sellers
(SaaS startups and other B2B vendors) who are selling into the Indian market**. India is
the moat play: we attack precisely where incumbents are weakest.

## Options considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| India leads → into-India sellers (chosen) | Registry moat (CIN/GSTIN); incumbents weak; cheap data | Smaller wallets; DPDP ambiguity | ✅ chosen |
| US/global leads | Bigger wallets, mature buyers | Crowded, incumbents strong, expensive data, no structural edge | rejected |
| India leads → global sellers targeting India later | Larger TAM eventually | Adds sales complexity before PMF | deferred — revisit post-P1 |

## Consequences

- **Positive:** a defensible data moat via registry anchoring; low data cost; a clear "we're
  the India experts" wedge for messaging.
- **Negative / cost:** exposure to DPDP/scraping legal ambiguity (RISKS.md#dpdp); an ICP
  with potentially smaller budgets (RISKS.md#small-wallet); entity-resolution edge cases for
  unregistered businesses / proprietorships without a CIN (QUESTIONS.md).
- **Follow-on:** forces ADR-004 (data via registry APIs) and ADR-005 (company-level first).

## Status history

- 2026-07-16 — accepted (co-founder interview)
