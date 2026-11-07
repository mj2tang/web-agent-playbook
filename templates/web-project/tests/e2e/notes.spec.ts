import { expect, test } from "@playwright/test";

test("a new user can sign up, add a note, delete it, and sign out", async ({ page }) => {
  const email = `e2e-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;
  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("correct-horse-battery");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page.getByRole("heading", { name: "Your notes" })).toBeVisible();
  await expect(page.getByText("No notes yet.")).toBeVisible();

  await page.getByLabel("New note").fill("Remember the milk");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page.getByRole("listitem").filter({ hasText: "Remember the milk" })).toBeVisible();
  await expect(page.getByText("Note saved.")).toBeVisible();

  await page.getByRole("button", { name: "Delete note: Remember the milk" }).click();
  await expect(page.getByText("No notes yet.")).toBeVisible();

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL("/"); // wait for sign-out to finish before checking the guard
  await page.goto("/notes");
  await expect(page).toHaveURL(/\/login$/);
});

test("validation errors are shown next to the field", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("not-an-email");
  await page.getByLabel("Password").fill("short");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByText("Enter a valid email address.")).toBeVisible();
  await expect(page.getByLabel("Email")).toHaveAttribute("aria-invalid", "true");
});
