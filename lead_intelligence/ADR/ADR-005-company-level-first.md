# ADR-005: Company-level intelligence first; person/contact data via compliant partners only

- **Status:** accepted *(founder-approved 2026-07-16)*
- **Date:** 2026-07-16
- **Deciders:** Founders (solo/duo)
- **Related:** ADR-001; ADR-004; RISKS.md#dpdp; ASSUMPTIONS.md#company-level-sellable; QUESTIONS.md#contact-data

## Context

The DPDP Act 2023 governs *personal* data. §3(c)(ii) exempts personal data that the data
principal has made publicly available — but government statements (notably in the Rajya Sabha,
Aug 2024) have signalled that *scraping* publicly-available personal data can still trigger
IT Act and DPDP obligations. The legal position is genuinely ambiguous (RISKS.md#dpdp, tracked
as a top-3 risk). Company-level facts (CIN, GSTIN, filings, funding, hiring at the org level)
are *not* personal data and sit far outside this ambiguity. Person-level contact data
(individual names, emails, phone) is exactly what the ambiguity bites.

## Decision

We will build and sell **company-level intelligence first**, and obtain any **person/contact
data only from compliant third-party providers** (not by scraping individuals ourselves).
This keeps our own data collection on the safe side of the DPDP ambiguity and pushes the
person-level compliance burden onto specialized providers.

## Options considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Company-level first; contacts via partners (chosen) | Minimizes DPDP surface; still sellable; partner owns person-level compliance | Contact data is a dependency/cost, not owned | ✅ chosen |
| Scrape person-level contacts ourselves | "Complete" record | Directly in DPDP/IT Act ambiguity; ToS traps (LinkedIn/Naukri) | rejected |
| No contact data at all | Zero person-level risk | May be unsellable if buyers need reachability | rejected — partial (partner path) |

## Consequences

- **Positive:** our first-party collection avoids the riskiest legal territory; the product's
  core value (why this account, why now) doesn't depend on person-level data.
- **Negative / cost:** buyers may still need contactability — so "build vs partner for contact
  data" stays an open decision (QUESTIONS.md#contact-data); relies on
  ASSUMPTIONS.md#company-level-sellable holding true.
- **Follow-on:** if company-level-only proves unsellable in P1, revisit with a vetted contact
  partner before any first-party person-level collection.

## Status history

- 2026-07-16 — proposed
- 2026-07-16 — accepted (founder approval)
