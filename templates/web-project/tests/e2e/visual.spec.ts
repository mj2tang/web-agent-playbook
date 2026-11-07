import { expect, test } from "@playwright/test";

// Runs at 1280 (desktop), 768 (tablet), and 375 (mobile) - see playwright.config.ts projects.
for (const route of ["/", "/login"]) {
  for (const colorScheme of ["light", "dark"] as const) {
    test(`@visual ${route} ${colorScheme}`, async ({ page }) => {
      await page.emulateMedia({ colorScheme });
      await page.goto(route);
      const name = route === "/" ? "home" : route.slice(1);
      await expect(page).toHaveScreenshot(`${name}-${colorScheme}.png`, { fullPage: true });
    });
  }
}
