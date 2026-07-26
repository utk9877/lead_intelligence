# Service runbook — deliver a researched account by hand

> How to produce ONE evidence-cited, scored account for a prospect (or a paying pilot
> customer) using the tools that already work — no autonomous crawler, no AWS, no
> database. This is your sales sample *and* your pilot delivery motion. You are the
> "automation" for now; that's deliberate (ADR-002).
>
> **Company-level facts only (ADR-005).** Never put a person's name, email, or phone
> in the signals. Job posts are "they're hiring" evidence, never individual records.

---

## One-time setup

1. An open-source model key (Groq is easiest/free) — see the main README quickstart
   and set `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `DRY_RUN_MODEL` (put them in `.env`).
2. `make sync` (installs the workspace). That's it — no database needed for this.

## Producing one account (≈10–15 minutes of your time)

### Step 1 — pick the target
Either the prospect names an Indian company they'd love to land, or you pick a
plausible one in their niche. This *is* the account you'll research.

### Step 2 — gather 2–4 real, public, company-level signals
Spend a few minutes finding genuine public buying signals, each with a **source URL**:
- **Funding:** a recent round (news sites, funding trackers). Source = the article URL.
- **Hiring surge:** open roles on their careers page or a job board. Source = the page.
- **Tech adoption:** their stack mentioned in job posts or on their site.
- **New incorporation / expansion / GST:** filings, a new-office news item.

Write each as a short factual sentence. **No individuals.** "They have 7 open SRE
roles" ✓. "Recruiter Priya's email is…" ✗ (and the system would reject it anyway).

### Step 3 — write the brief
Copy `docs/gtm/example-target.json` to a new file (e.g. `brief.json`) and fill in:
- `company`: name, and CIN/GSTIN/domain if you have them.
- `customer`: the *prospect's* offering and who they target (this is what "fit" is
  judged against — get it right, it's what makes the research land).
- `observations`: your 2–4 signals, each with its real `source_url`.

### Step 4 — run it
```
uv run python tools/research_company.py brief.json
```
The three-pass pipeline runs (triggers → deep-fit research → scoring) and prints:
- the buying **triggers** it detected,
- an evidence-cited **why-now / why-fit** narrative,
- each **claim tied to your source URL**,
- a **warm/hot score** with rationale, and the model cost for the account.

Every claim is forced to cite one of your sources — the system refuses to emit an
uncited claim, so the output is defensible by construction.

### Step 5 — you are the QA gate
Read it. This is the human-review step that every delivered account passes (ADR-002,
`ARCHITECTURE.md` §9). Check: are the claims accurate? Does the "why now" hold up?
Is the fit reasoning real? Fix or tighten wording; drop anything shaky. If the model
produced weak output, add stronger signals and re-run, or try a stronger model.

### Step 6 — package and send
Paste the cleaned account into a short, branded email/Slack message:
> **{Company} — WARM ({score}/100)**
> *Why now:* …
> *Why they fit you:* …
> *Evidence:* • claim — [source] • claim — [source]
Send it to the prospect within a day of the call. This sample is your strongest
sales asset — it shows the *worked conclusion*, not a database (the whole positioning,
`PROJECT_SPEC.md` §3; the wedge vs Pintel, `COMPETITOR_ANALYSIS.md`).

## Delivering a paid pilot

Same loop, at volume: agree N accounts/month with the customer, produce them in
batches through Step 1–6, deliver to their Slack/email. **Track two numbers** — the
minutes you spend per account and the model cost per account — because those are the
P1 metrics that tell you the economics work before you automate (`PROJECT_SPEC.md`
§6, `ASSUMPTIONS.md#delivery-capacity`, `#api-cost`). Also capture their feedback
(which accounts they pursued) — that's the labelled data that will train the
automated scorer later.

## Optional: show the reviewer console

If you want to demo the review-and-approve experience, bring up the QA console
(`make up && make migrate`, then `make api` + `make console`, open localhost:3000).
It's the internal gate a human uses at scale — useful to show a prospect where this
is heading, but not needed to deliver the manual service.

## What NOT to do yet
- Don't crawl live sites in bulk — the allow-list is empty by design and needs a
  ToS/legal check first (`RISKS.md#data-tos`, `#dpdp`). For the manual service you
  read public pages yourself and cite the URL; that's fine.
- Don't scrape person-level data anywhere. Ever.

---

**Related:** `discovery-playbook.md` (booking the calls) · `tools/research_company.py`
(the engine) · `docs/gtm/example-target.json` (brief format) · `PROJECT_SPEC.md` §3,§6.
