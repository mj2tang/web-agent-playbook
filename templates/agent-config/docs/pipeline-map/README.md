# Pipeline map — {{project}}

Behaviour-level inventory of every way this app is used. Agents use it to decide **what to run** and **what evidence counts** when proving a change works (`prove-it-works` skill); humans use it as the regression checklist. One short file per entry point; keep entries runnable without reading source.

Each file answers the same four questions:
1. **What it is** — the entry point and who/what uses it.
2. **How to reach it** — commands or requests a real user/system makes.
3. **Evidence that counts** — the artifact a skeptical reviewer would accept.
4. **What usually lies** — known ways it looks fine but isn't.

## Baseline preconditions
- `pnpm install` done from the committed lockfile; local Supabase running (`pnpm exec supabase start`) and reset (`supabase db reset`) so the seed is fresh.
- Run from the task's worktree on its committed HEAD; `pnpm build && pnpm start` for anything performance- or cache-related, `pnpm dev` otherwise.

## Proof rules
- Exercise a change through **every entry point it can affect**, not just the one its unit test covers. A shared component touches every route that renders it; a migration touches every route that reads the table.
- Always include the **signed-out** and **other user** paths for anything behind auth.
- Record each command and its artifact in the decision trail (`scripts/agent-team/audit.py log ...`).
- When an entry point can't be exercised here (production data, third-party webhook, deployed env), name it, say what blocks it, and cover the closest real path.

## Full sweep
1. [routes](routes.md) — pages users load
2. [server-actions-api](server-actions-api.md) — mutations and HTTP endpoints
3. [database-rls](database-rls.md) — schema, policies, functions
4. [auth](auth.md) — sign-in, sessions, protected routes
5. [jobs](jobs.md) — edge functions, cron, webhooks

Add files as the app grows (payments, email, search). Fix drift in the same PR as the change that caused it.
