---
name: prove-it-works
description: Prove a change works on the running app before calling it done - exercise every pipeline-map entry point the change can affect (routes, server actions and API, database and RLS, auth, background jobs) against local Supabase, capture evidence a skeptical reviewer would accept (screenshots, Playwright and pgTAP output, curl transcripts), and verify delegated work from artifacts, never from the delegate's summary. Use before marking any task done or approving a worker's branch. Not for read-only questions or pure planning.
---

# Prove it works

Passing unit tests and "it builds" are proxies. Proof means running the real path and reading the real result.

## 1. Pick the coverage set
Read `docs/pipeline-map/README.md`, then every entry-point file your change can affect. A component change touches **routes** (every page that renders it). A server action touches **server-actions-api** and usually **database-rls**. A migration touches **database-rls** and every route that reads that table. Anything near sessions touches **auth**.

## 2. Exercise each entry point
Run the commands in each file's "How to reach it" on this branch's HEAD, against local Supabase (`supabase start`) and `pnpm dev` or `pnpm build && pnpm start`. Cover the paths the change can affect: success, empty state, invalid input, signed out, and **another user's data** (must be denied).

## 3. Capture evidence
For each entry point, record what the file's "Evidence that counts" names: screenshots at 375/768/1280 (light and dark) with their paths, the Playwright report, the axe result, the pgTAP output, a `curl -i` transcript showing status codes. Log one row per entry point:

```
python3 scripts/agent-team/audit.py log verify T-012 frontend-worker "playwright + axe on HEAD" "covers routes: /notes" "playwright-report/index.html" "ui-check: PASS"
```

## 4. Check "what usually lies"
Each pipeline-map file lists known false positives: a dev server still serving the old build, a test that ran as the service role (bypasses RLS), a screenshot of the cached page, types generated before the last migration. Rule each one out explicitly.

## 5. Unreachable paths
If an entry point needs production data, a third-party webhook, or a deployed environment, name it, say what blocks it, and cover the closest real path (a recorded payload against the local route handler). Never claim coverage you didn't run.

## Verifying someone else's work
Agents report what they intended, not always what happened. Re-run the gates yourself, open the screenshots and reports, and confirm they were produced from the branch HEAD. A summary without matching artifacts is not proof.

## When the proof can be scripted
Prefer a Playwright spec or pgTAP test that re-runs the check over a one-time look; the script is the artifact a reviewer re-runs.

Adapted from Lauren Tan's "prove it works" principle and feature-map verification in pstack.
