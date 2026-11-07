# Routes (pages)

## What it is
Every page under `src/app/` that a user loads: `/`, `/login`, `/notes`, ... (keep this list current).

## How to reach it
- `pnpm exec playwright test tests/e2e/` against `pnpm dev` (config starts the server).
- Interactive: Playwright MCP `browser_navigate` + `browser_take_screenshot` at 375/768/1280, light and dark.

## Evidence that counts
- Playwright report with the route's spec passing; axe result with zero serious/critical issues.
- Screenshots of each state in the component spec (empty, loading, error, filled), named `<route>-<state>-<width>-<theme>.png`.

## What usually lies
- A dev server started before your change (stale HMR state) — restart it.
- Screenshots of the signed-out page when the change is behind auth.
- A passing e2e that never waited for data (`expect(...).toBeVisible()` missing) — check the screenshot shows real content.
