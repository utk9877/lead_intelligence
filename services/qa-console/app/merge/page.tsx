"use client";

import { useEffect, useState } from "react";
import { MergeCandidate, getMergeQueue } from "@/lib/api";

export default function MergeQueuePage() {
  const [candidates, setCandidates] = useState<MergeCandidate[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMergeQueue().then(setCandidates).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p role="alert">{error}</p>;

  return (
    <div>
      <h1>Merge queue</h1>
      <p style={{ color: "var(--muted)", fontSize: "0.85rem" }}>
        Ambiguous or conflicting entity resolutions awaiting a human merge decision.
      </p>
      {candidates.length === 0 ? (
        <p data-testid="empty">Nothing to merge.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Source</th>
              <th>Hint</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((c) => (
              <tr key={c.id} data-testid="candidate">
                <td>{c.raw_name}</td>
                <td>{c.source}</td>
                <td>{c.candidate_company_id ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
