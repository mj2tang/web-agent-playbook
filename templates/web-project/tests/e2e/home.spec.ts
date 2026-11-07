import { expect, test } from "@playwright/test";

test("home explains the app and links to notes", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await page.getByRole("link", { name: "Open your notes" }).click();
  await expect(page).toHaveURL(/\/login$/); // signed out: the notes page sends you to sign in
});

test("health route reports the database", async ({ request }) => {
  const res = await request.get("/api/health");
  expect(res.status()).toBe(200);
  expect(await res.json()).toEqual({ db: "ok" });
});
