// Typed client for the internal API, via the same-origin server proxy.

export interface AccountSummary {
  score_id: string;
  company_id: string;
  customer_id: string;
  company_name: string;
  value: string;
  band: string;
  rubric_version: string;
  model_version: string;
}

export interface MergeCandidate {
  id: string;
  source: string;
  raw_name: string;
  candidate_company_id: string | null;
  status: string;
}

export interface CostSummary {
  total_inr: string;
  by_stage: Record<string, string>;
}

export type ReviewDecision = "approve" | "reject" | "edit";

const base = "/api/backend";

export async function getReviewQueue(): Promise<AccountSummary[]> {
  const res = await fetch(`${base}/qa/queue`, { cache: "no-store" });
  if (!res.ok) throw new Error(`queue failed: ${res.status}`);
  return res.json();
}

export async function getMergeQueue(): Promise<MergeCandidate[]> {
  const res = await fetch(`${base}/qa/merge-queue`, { cache: "no-store" });
  if (!res.ok) throw new Error(`merge-queue failed: ${res.status}`);
  return res.json();
}

export async function getCosts(): Promise<CostSummary> {
  const res = await fetch(`${base}/costs`, { cache: "no-store" });
  if (!res.ok) throw new Error(`costs failed: ${res.status}`);
  return res.json();
}

export async function recordReview(input: {
  company_id: string;
  customer_id: string;
  reviewer: string;
  decision: ReviewDecision;
  notes?: string;
}): Promise<void> {
  const res = await fetch(`${base}/qa/review`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error(`review failed: ${res.status}`);
}
