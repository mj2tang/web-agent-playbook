// Installed by web-agent-playbook. Add every route to ROUTES; the gate fails on serious/critical axe issues.
import { readFileSync } from "node:fs";
import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

// Which axe impacts fail the gate: configs/gates.json (human-approved changes only).
const FAIL_ON: string[] = JSON.parse(readFileSync("configs/gates.json", "utf8")).a11y.fail_on_impact;

const ROUTES = ["/"];

for (const route of ROUTES) {
  for (const colorScheme of ["light", "dark"] as const) {
    test(`a11y ${route} (${colorScheme})`, async ({ page }) => {
      await page.emulateMedia({ colorScheme });
      await page.goto(route);
      const { violations } = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]).analyze();
      const blocking = violations.filter((v) => FAIL_ON.includes(v.impact ?? ""));
      expect(blocking.map((v) => `${v.id}: ${v.help} (${v.nodes.length})`)).toEqual([]);
    });
  }
}

test("no horizontal scroll at 320px", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  for (const route of ROUTES) {
    await page.goto(route);
    const width = await page.evaluate(() => document.documentElement.scrollWidth);
    expect(width, route).toBeLessThanOrEqual(320);
  }
});
