"use client";

import { useEffect, useState } from "react";
import {
  AccountSummary,
  ReviewDecision,
  getReviewQueue,
  recordReview,
} from "@/lib/api";

export default function ReviewQueuePage() {
  const [accounts, setAccounts] = useState<AccountSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  async function load() {
    try {
      setAccounts(await getReviewQueue());
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function decide(account: AccountSummary, decision: ReviewDecision) {
    setBusy(account.score_id);
    try {
      await recordReview({
        company_id: account.company_id,
        customer_id: account.customer_id,
        reviewer: "reviewer",
        decision,
      });
      // Once reviewed, the account leaves the queue.
      setAccounts((prev) => prev.filter((a) => a.score_id !== account.score_id));
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <h1>Review queue</h1>
      {error && <p role="alert">{error}</p>}
      {accounts.length === 0 && !error ? (
        <p data-testid="empty">No accounts awaiting review.</p>
      ) : null}
      {accounts.map((a) => (
        <div className="card" key={a.score_id} data-testid="account">
          <div>
            <span className={`band ${a.band}`}>{a.band}</span> · score {a.value}
          </div>
          <h3>{a.company_name}</h3>
          <div style={{ color: "var(--muted)", fontSize: "0.8rem" }}>
            rubric {a.rubric_version} · model {a.model_version}
          </div>
          <div style={{ marginTop: "0.75rem" }}>
            <button disabled={busy === a.score_id} onClick={() => decide(a, "approve")}>
              Approve
            </button>
            <button
              className="reject"
              disabled={busy === a.score_id}
              onClick={() => decide(a, "reject")}
            >
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
