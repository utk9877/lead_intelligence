"use client";

import { useEffect, useState } from "react";
import { CostSummary, getCosts } from "@/lib/api";

export default function CostBoardPage() {
  const [costs, setCosts] = useState<CostSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCosts().then(setCosts).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p role="alert">{error}</p>;
  if (!costs) return <p>Loading…</p>;

  return (
    <div>
      <h1>Cost board</h1>
      <p data-testid="total">
        Total: ₹{costs.total_inr}{" "}
        <span style={{ color: "var(--muted)", fontSize: "0.8rem" }}>
          (illustrative — placeholder economics)
        </span>
      </p>
      <table>
        <thead>
          <tr>
            <th>Stage</th>
            <th>₹</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(costs.by_stage).map(([stage, amount]) => (
            <tr key={stage}>
              <td>{stage}</td>
              <td>{amount}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
