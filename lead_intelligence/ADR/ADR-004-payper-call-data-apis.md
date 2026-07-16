# ADR-004: Data via pay-per-call registry APIs + own compliant crawling; no enterprise licenses

- **Status:** proposed *(awaiting founder approval)*
- **Date:** 2026-07-16
- **Deciders:** Founders (solo/duo)
- **Related:** ADR-001; ADR-005; ASSUMPTIONS.md#api-cost; RISKS.md#dpdp; RISKS.md#data-tos

## Context

The bootstrap constraint (ADR context: no big-data licenses, revenue-funded) rules out
enterprise data licenses (ZoomInfo/Apollo-scale contracts). But India's registry data is
reachable another way: **MCA (Ministry of Corporate Affairs) and GST data are available via
cheap pay-per-call APIs** from a class of vendors — Attestr, Surepass, Karza, Signzy and
similar — priced per lookup rather than per seat/year. Combined with our own crawling of
public sources (company sites, news, job posts), this is enough to build the
registry-anchored company graph.

## Decision

We will source data through (a) **pay-per-call registry/verification APIs** for
CIN/GSTIN-anchored company facts, and (b) **our own compliant crawling** of public web
sources — and we will **not** buy enterprise data licenses in Phase 1. Cost per account is
tracked as a first-class unit-economics metric (PROJECT_SPEC.md success metrics).

## Options considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Pay-per-call APIs + own crawl (chosen) | Bootstrap-viable; pay for what we use; registry-anchored | Per-call cost scales with volume; crawl ToS risk | ✅ chosen |
| Enterprise data license | Breadth, one contract | Unaffordable bootstrapped; US-centric coverage | rejected |
| Pure scraping, no paid APIs | Cheapest | Higher legal exposure (RISKS.md#dpdp/#data-tos); no clean registry key | rejected |

## Consequences

- **Positive:** no upfront license cost; costs track revenue; registry APIs give the clean
  CIN/GSTIN key that anchors entity resolution (ADR-001's moat).
- **Negative / cost:** per-call pricing means margin is volume-sensitive
  (ASSUMPTIONS.md#api-cost, RISKS.md#llm-cost); own crawling carries ToS/DPDP exposure
  (RISKS.md#data-tos, RISKS.md#dpdp) — crawl only public, company-level data (ADR-005).
- **Follow-on:** tightly couples to ADR-005 (company-level, not person-level, to reduce legal
  surface).

## Status history

- 2026-07-16 — proposed
