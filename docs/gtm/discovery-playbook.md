# Discovery & sell-this-week playbook

> **Goal:** book 15–20 discovery calls, find ≥3 buyers who'll pay for a pilot, and
> land your first design partner — *without building the autonomous crawler first*.
> This is the P0 learning gate in `ROADMAP.md`. You sell the **service** (delivered,
> researched, evidence-cited accounts) and run it semi-manually with the tools that
> already work. Automate later, with a paying customer's money and feedback.
>
> **All prices below are illustrative placeholders to test in the calls, not
> commitments** (repo convention; see `PROJECT_SPEC.md` §5, `QUESTIONS.md#pricing`).

---

## 1. Who you're selling to (the ICP)

**Your customer is a B2B vendor selling INTO India** — most cleanly a B2B SaaS
startup, or an agency/services firm, whose deals are big enough to justify paying
for researched accounts. Not the Indian companies themselves — *the people selling
to them* (ADR-001, `PROJECT_SPEC.md` §2).

They feel the pain when: their team is small, Apollo/ZoomInfo are stale on India and
weak on sub-200-employee companies, and they waste selling time on bad-fit accounts.

**Pick ONE starting niche to make outreach concrete** (you'll refine it in the calls —
it is *not* a final decision, `QUESTIONS.md#niche`). Cleanest opening bet from the
scoring in `PROJECT_SPEC.md` §7: **sellers targeting funded / scaling Indian SMBs**
(the trigger stack — funding + hiring + incorporation — is richest and the sellers
are reachable through the startup ecosystem). D2C/e-commerce sellers are the strong
alternative.

## 2. Where to find them (this week)

- **LinkedIn:** founders / heads-of-sales / SDR leads at B2B SaaS companies whose
  product page says "for Indian businesses" or who are clearly selling into India.
  Search titles + "India" + their category.
- **Startup communities:** SaaSBoomi, India SaaS groups, Indie Hackers India,
  relevant Slack/WhatsApp/Discord communities, r/indiabusiness.
- **Your own network first.** The warmest 5 calls you can get this week beat 50 cold
  ones. Anyone you know selling B2B into India → ask them, and ask for one intro each.
- **Agencies** selling websites/marketing/software to Indian SMBs (your own example:
  the web-services agency selling to local businesses).

Aim for a list of ~40 names to get ~15–20 calls.

## 3. Outreach templates

Keep it short, specific, and **lead with a free sample** — the sample is your whole
sales motion (see `service-runbook.md`). Don't pitch the software; offer the outcome.

**LinkedIn / email (cold):**

> Subject: a researched account for {their company}, on me
>
> Hi {name} — you sell {their product} into India. Finding which Indian companies
> are actually in a buying window (and why) is slow with US-first tools.
>
> I research Indian companies and deliver warm, scored accounts with an evidence-cited
> "why this account, why now" — the worked conclusion, not a database to dig through.
>
> Want me to research one account you'd love to land, free, so you can see the
> quality? Just name a target Indian company (or a type), and I'll send it over.

**Warm intro / network:**

> Quick ask — do you know anyone selling B2B into India who struggles to find good-fit
> accounts? I'm building a service that delivers researched, warm Indian-company
> accounts and I'm looking for a few people to give me 20 minutes and (if they like it)
> a free sample.

The reply-magnet is the **free researched account**. When they name a target, produce
it with `service-runbook.md` and send it back within a day.

## 4. The discovery call (20–25 min)

**Rule: don't pitch. Learn about their world.** You're testing whether the pain is
real and whether they'll pay — not convincing them. (If you've read *The Mom Test*,
this is that.) Talk 20% of the time.

**Warm-up / context**
- "Tell me how you sell into India today — who's your ideal customer there?"
- "How do you find and pick which accounts to go after each month?"
- "What tools do you use for that? What do they cost you?"

**Dig into the pain (past behaviour, not hypotheticals)**
- "Walk me through the last time you spent real effort on an account that turned out
  to be a bad fit. What happened?"
- "How do you know when an Indian company is actually worth a call *right now*?"
- "What's the most frustrating part of building your India pipeline?"

**Test the shape of the offer**
- "If someone handed you, each month, N Indian companies that are in a buying window —
  each with an evidence-cited reason why them and why now, already scored — how would
  that change your week?"
- "What would make that a must-have vs a nice-to-have for you?"
- "Who else would need to say yes to bring something like this in?"

**Test willingness to pay (do NOT skip this)**
- "Roughly what do you spend today on prospecting tools + the people-time to work
  them?"
- "If a pilot delivered N researched warm accounts a month, what would feel fair —
  and would you run a paid pilot for a month at, say, {illustrative ₹ figure — to
  validate, PROJECT_SPEC.md §5}?"
- Watch for real signals: they ask "how soon can we start?", they name a budget
  unprompted, they offer to introduce you. Vague enthusiasm ("cool idea!") is a *no*.

**Close the call**
- "Can I research one account for you free this week so you can judge the quality?"
- "If it's useful, would you pilot it for a month?"

## 5. Qualify — is this a real design partner?

A yes needs all four:
- [ ] **Selling INTO India** (B2B), small enough team to feel the pain.
- [ ] **Named the pain unprompted** or told a real bad-fit-account story.
- [ ] **Has budget** (spends on tools/prospecting today).
- [ ] **Willing to pilot** — ideally paid, at minimum a firm committed pilot.

Log every call in a simple sheet: name, company, do-they-sell-into-India, pain quote,
budget signal, pilot-yes/no. Three checked-all-four = your P0 gate is met.

## 6. The pilot offer (illustrative — validate in the calls)

- **Shape:** "N researched, scored, warm accounts in your niche this month, delivered
  to your Slack/email, each with an evidence-cited why-now — behind my human review."
- **N and price are placeholders** to test (`QUESTIONS.md#target-n`, `#pricing`). Start
  by asking *them* what N and price feel right; don't lead with a number.
- **Delivery:** you run the service by hand for the pilot (`service-runbook.md`). You
  are the automation. That's fine — it's how you learn what "warm" means for them
  before you automate (ADR-002).

## 7. What "done" looks like for P0

Per `ROADMAP.md#design-partner`: one committed design partner in the niche they
demand + ≥3 buyers willing to pay + at least one real batch of accounts delivered
with a *measured* cost-per-account. Then — and only then — you build the autonomous
crawler and deploy to AWS.

---

**Related:** `service-runbook.md` (how to produce a deliverable) · `PROJECT_SPEC.md`
(positioning, ICP, niches) · `COMPETITOR_ANALYSIS.md` (why you win vs Pintel) ·
`ROADMAP.md` (the P0 gate) · `QUESTIONS.md` (open pricing/niche/N decisions).
