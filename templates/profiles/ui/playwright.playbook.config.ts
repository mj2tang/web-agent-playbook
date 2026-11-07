// Installed by web-agent-playbook: a standalone Playwright config for the playbook's a11y and visual checks.
// Your own playwright.config.* is untouched; scripts/gates/ui-check.sh prefers this file when present.
import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PLAYBOOK_BASE_URL ?? "http://localhost:3000";

export default defineConfig({
  testDir: "./tests/e2e-playbook",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report-playbook" }]],
  use: { baseURL, trace: "retain-on-failure" },
  projects: [
    { name: "mobile", use: { ...devices["Desktop Chrome"], viewport: { width: 375, height: 812 } } },
    { name: "tablet", use: { ...devices["Desktop Chrome"], viewport: { width: 768, height: 1024 } } },
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } },
  ],
  webServer: process.env.PLAYBOOK_BASE_URL
    ? undefined
    : { command: process.env.PLAYBOOK_DEV_CMD ?? "npm run dev", url: baseURL, reuseExistingServer: true },
});
