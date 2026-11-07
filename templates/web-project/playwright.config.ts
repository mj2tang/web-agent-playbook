import { readFileSync } from "node:fs";
import { defineConfig, devices } from "@playwright/test";

// Thresholds come from configs/gates.json (human-approved changes only).
const gates = JSON.parse(readFileSync("configs/gates.json", "utf8"));

const port = Number(process.env.PORT ?? 3000);
const baseURL = `http://localhost:${port}`;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [["list"], ["html", { open: "never" }]],
  // Baselines are written only on purpose (`make baselines`, a human step) and committed; a missing
  // baseline fails the gate instead of silently passing.
  updateSnapshots: process.env.UPDATE_BASELINES === "1" ? "missing" : "none",
  expect: { toHaveScreenshot: { maxDiffPixelRatio: gates.visual.max_diff_pixel_ratio, animations: "disabled" } },
  use: { baseURL, trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } },
    { name: "tablet", grep: /@visual/, use: { ...devices["Desktop Chrome"], viewport: { width: 768, height: 1024 } } },
    { name: "mobile", grep: /@visual/, use: { ...devices["Desktop Chrome"], viewport: { width: 375, height: 812 } } },
  ],
  webServer: {
    command: `pnpm build && pnpm start --port ${port}`,
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
  },
});
