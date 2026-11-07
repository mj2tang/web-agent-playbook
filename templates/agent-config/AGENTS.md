# AGENTS.md — {{project}}

{{description}}

## Commands
- Install: `pnpm install` (lockfile committed; don't add packages without approval)
- Dev: `pnpm dev` · Local Supabase: `pnpm exec supabase start` / `status` / `stop` (Docker)
- Lint + types + unit: `make check` (no Makefile: `scripts/gates/check.sh`)
- Design lint: `make design-check` (`scripts/gates/design-check.sh`): tokens not raw values, focus kept, real buttons/links, no generic-AI patterns
- Database: `make db-check` - `supabase db reset`, pgTAP (`supabase test db`), RLS on every table, generated types up to date (`scripts/gates/db-check.sh`)
- UI: `make ui-check` - Playwright e2e, axe, screenshots at 375/768/1280 (`scripts/gates/ui-check.sh`)
- Performance: `make perf` - Lighthouse budgets from `configs/gates.json`
- One unit test: `pnpm exec vitest run tests/unit/x.test.ts` · one e2e: `pnpm exec playwright test tests/e2e/x.spec.ts`
- New migration: `pnpm exec supabase migration new <name>` · types: `pnpm run db:types`

## Layout
- `src/app/` routes (server components by default) · `src/components/` shared UI · `src/styles/tokens.css` design tokens
- `src/lib/supabase/` server/browser clients + session-refresh helper for `src/proxy.ts` · `src/lib/server/` server-only code · `src/lib/contracts/` Zod schemas · `src/lib/database.types.ts` generated
- `supabase/migrations/` schema + RLS · `supabase/tests/` pgTAP · `supabase/seed.sql` local data
- `tests/unit/` Vitest · `tests/e2e/` Playwright (+ axe, `@visual` screenshots)
- `PRODUCT.md` + `DESIGN.md` (repo root) design context · `docs/design/` system design, component specs · `docs/pipeline-map/` entry points and proof · `docs/solutions/` lessons learned (read before planning)
- `tasks/` agent task board · `configs/` team and gate budgets

## Conventions
- Read `DESIGN.md` before UI work. Style with tokens only: no raw hex/rgb or arbitrary px in components; new tokens come from the ui-designer.
- `"use client"` only on leaves that need state, effects, or browser APIs.
- Every server action and route handler validates input with the contract's Zod schema and calls `supabase.auth.getUser()` before acting.
- Every table in `public` has RLS enabled, explicit policies per role and operation, and pgTAP tests for allow and deny.
- Schema changes only through new migrations; never edit an applied one. Regenerate types in the same commit.
- Next.js 16+: APIs differ from older versions (`proxy.ts` replaced `middleware.ts`). Read `node_modules/next/dist/docs/` before using an API you haven't checked.
- Accessible by default: semantic HTML, labels, visible focus, axe clean, keyboard-only path works.
- Commits: `T-<id>: <what>` for task work; `contract: ...` and `design: ...` for wave-0 work.

## Allowed without asking
- Any `make` target and `scripts/gates/*`; `pnpm install` (no new packages), `pnpm run *`, `pnpm exec vitest|playwright test|tsc|eslint`.
- Local Supabase: `supabase start|stop|status|db reset|test db|migration new|gen types --local|db push --local`.
- Create branches and worktrees named `task/*`, commit on them, and merge approved task branches into `main` locally.
- Write to `tasks/`, `docs/design/` (architect/designer), test files, and the task's owned files.

## Needs human approval
- `git push`, deploys (`vercel`, `netlify`), and **anything touching a linked or remote Supabase project** (`link`, `db push` without `--local`, `functions deploy`, `secrets set`, `--db-url`, `--project-ref`).
- Using `SUPABASE_SERVICE_ROLE_KEY` anywhere new; it bypasses RLS.
- Adding or upgrading dependencies.
- Editing a committed migration or migration history (`migration repair`).
- Writing or updating visual baselines (`make baselines`, `--update-snapshots`), or changing `configs/gates.json` or the Playwright config.

## Proof and trail
- Prove changes on the running app through every affected entry point in `docs/pipeline-map/` (`prove-it-works`); keep the map current in the same PR.
- Log decisions with `python3 scripts/agent-team/audit.py log ...` (`.audit/decisions.tsv`, local). Parallelism follows `audit.py trust`.
- A gate that prints `SKIPPED` is not a pass.

## Agent team
- Wave 0: `system-architect` freezes the contract (design doc, migrations + RLS + pgTAP, types, Zod schemas); `ui-designer` the brief, tokens, and component specs. Workers build against them and never change them.
- Orchestrator (`claude --agent orchestrator`, or `$orchestrate-team` in Codex) plans tasks and dispatches `frontend-worker` / `backend-worker`, each in its own worktree on `task/<id>-<slug>`; `supervisor` reviews every branch, with `security-reviewer` for auth/RLS/server actions and `a11y-reviewer` for UI. Protocols: skills `orchestrate-team`, `worker-protocol`, `merge-train`.
- Read `tasks/<id>.md` before working on a task; keep its status current.
- Codex: the roles are native agents in `.codex/agents/`; spawn them by name ("spawn the `backend-worker` agent for tasks/T-002-..."), since Codex never spawns custom agents on its own. Guard hooks run only after you trust them once (`/hooks`). Headless workers: `RUNNER=codex scripts/agent-team/run-wave.sh T-001` (no network, runner commits). Codex supervisor: `codex exec --sandbox workspace-write -c sandbox_workspace_write.network_access=true --add-dir <worktree> "Act as the supervisor in .claude/agents/supervisor.md ..."`.

## Code Review Rules
### Authorization
- Flag any new table without `enable row level security`, policies per operation, and a pgTAP deny test.
- Flag policies without `with check` on insert/update, policies `to public`, and `user_metadata` in policies.
- Flag server actions and route handlers that don't call `auth.getUser()` or trust a client-supplied owner/user ID.
### Secrets
- Flag `SUPABASE_SERVICE_ROLE_KEY` or `service_role` outside `server-only` modules, secrets in `NEXT_PUBLIC_*`, and `.env` files in the diff.
### Contract drift
- Flag hand-edited `database.types.ts`, redeclared shapes instead of contract imports, edits to committed migrations, and Zod limits that differ from database constraints.
### UI quality
- Flag raw hex/px in components, missing states from the component spec, `div` buttons, missing labels, removed focus styles, and new client components at layout/page roots.
### Gate integrity
- Flag changes to `configs/gates.json`, snapshot files, `test.skip`/`.only`, `eslint-disable`, `@ts-expect-error`, or axe rule disables unless the PR says why and a human approved it.
