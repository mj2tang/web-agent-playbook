import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

// Every route belongs here (accessibility-audit skill). The gate fails on serious or critical issues.
const ROUTES = ["/", "/login"];

for (const route of ROUTES) {
  for (const colorScheme of ["light", "dark"] as const) {
    test(`axe: ${route} (${colorScheme})`, async ({ page }) => {
      await page.emulateMedia({ colorScheme });
      await page.goto(route);
      const { violations } = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();
      const blocking = violations.filter((v) => v.impact === "serious" || v.impact === "critical");
      expect(blocking.map((v) => `${v.id}: ${v.help} (${v.nodes.length} nodes)`)).toEqual([]);
    });
  }
}

test("no horizontal scroll at 320px", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  for (const route of ROUTES) {
    await page.goto(route);
    expect(await page.evaluate(() => document.documentElement.scrollWidth), route).toBeLessThanOrEqual(320);
  }
});

test("keyboard: skip link moves focus to main content", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
});
