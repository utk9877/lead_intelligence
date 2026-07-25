import { expect, test } from "@playwright/test";

const ACCOUNT = {
  score_id: "s1",
  company_id: "11111111-1111-1111-1111-111111111111",
  customer_id: "22222222-2222-2222-2222-222222222222",
  company_name: "Fictional Widgets Pvt Ltd",
  value: "80.00",
  band: "warm",
  rubric_version: "r1",
  model_version: "claude-sonnet-5",
};

test("reviewer sees the queue, approves an account, and it leaves the queue", async ({
  page,
}) => {
  await page.route("**/api/backend/qa/queue", (route) =>
    route.fulfill({ json: [ACCOUNT] }),
  );
  let reviewBody: unknown = null;
  await page.route("**/api/backend/qa/review", async (route) => {
    reviewBody = route.request().postDataJSON();
    await route.fulfill({ json: { id: "r1", decision: "approve" } });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Fictional Widgets Pvt Ltd" })).toBeVisible();
  await expect(page.getByText("warm")).toBeVisible();

  await page.getByRole("button", { name: "Approve" }).click();

  // The approved account leaves the queue, and the review was posted with the ids.
  await expect(page.getByTestId("account")).toHaveCount(0);
  await expect(page.getByTestId("empty")).toBeVisible();
  expect(reviewBody).toMatchObject({
    decision: "approve",
    score_id: ACCOUNT.score_id,
    company_id: ACCOUNT.company_id,
  });
});

test("cost board renders the ledger rollup", async ({ page }) => {
  await page.route("**/api/backend/costs", (route) =>
    route.fulfill({
      json: { total_inr: "249.00", by_stage: { pass1_triggers: "83.00", pass2_research: "166.00" } },
    }),
  );
  await page.goto("/costs");
  await expect(page.getByTestId("total")).toContainText("₹249.00");
  await expect(page.getByText("pass2_research")).toBeVisible();
});
