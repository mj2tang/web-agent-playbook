# web-agent-playbook — design

Date: 2026-11-07 · Owner: mj2tang · Status: draft for approval

## Intent

A public GitHub repo, `mj2tang/web-agent-playbook`, that is the **scaffolding other web projects plug into** to get an optimised coding-agent setup for full-stack web work — website/UI design, frontend, and backend architecture — with **Codex and Claude Code** sharing one set of skills. It is the web sibling of `mj2tang/coding-agent-playbook` (the ML playbook): same shape (agent team, skills, guardrail hooks, scaffolder, task board, trust ladder), web-specific content.

Nobody builds sites *in* this repo. You run `init` against an existing repo, or `new` to get a starter app, and the project gets the agent setup.

## Goals

1. **Plug into any web repo** (`init .`): additive only, never edits the user's own `AGENTS.md`/`CLAUDE.md`, source, or structure — same contract and same `check_install_safety.py` proof as the ML playbook.
2. **Optimised Codex setup**: `AGENTS.md` with web rules and Code Review Rules, `.agents/skills/`, a project `.codex/config.toml` (sandbox/approval defaults, MCP servers), Codex plugin + marketplace manifests, `RUNNER=codex` headless waves.
3. **Same for Claude Code**: `CLAUDE.md` → `@AGENTS.md`, `.claude/agents/`, `.claude/skills/` (symlink), `.claude/settings.json` permissions + guard hooks, Claude plugin + marketplace manifests.
4. **Design + frontend + backend coverage** in skills, roles, and gates (below).
5. **Supabase/Postgres starter** (`new`): a runnable app that is green on first run.
6. **Agents can check their own work** in seconds: lint, types, unit, pgTAP, accessibility, visual snapshots.

## Non-goals

- Not a component library or design system product — it teaches agents to build/keep one per project.
- No hosting/deploy automation (Vercel etc.) beyond a human-gated checklist skill.
- Not a fork of the ML playbook; no ML content (MLflow, Databricks, model evaluators).
- No backend other than Supabase in the starter (existing repos with other backends still get the stack-agnostic skills).

## Anti-goals (failure even if it "works")

- `init` modifies or deletes any existing file in the user's repo.
- Agents can reach a linked/remote Supabase project, use the service-role key, push, or deploy without a human.
- A migration that disables RLS, or a table without RLS, passes the gates.
- Agents get green by editing snapshots, a11y thresholds, or tests.
- Generic "AI-looking" UI: the design skills must push for a project-specific design system (tokens first), not default gradients.

## What ships

### Agent team (`agents/`, rendered into `.claude/agents/`; plain markdown Codex can use)
| Role | Job |
|---|---|
| `orchestrator` | Main session: reads `tasks/EPIC.md`, writes task files, dispatches workers, routes reviews, runs the merge train |
| `system-architect` | Writes the system design doc and **freezes the API/data contract** (SQL schema + RLS + typed API surface) before workers start. Read-only on app code |
| `ui-designer` | Design brief → design tokens → page/component specs with states; reviews screenshots for fidelity |
| `frontend-worker` | Builds UI against the frozen contract (`isolation: worktree`) |
| `backend-worker` | Migrations, RLS, RPC/Edge Functions, server actions (`isolation: worktree`) |
| `supervisor` | Read-only gatekeeper: runs gates in the worker's checkout, checks evidence, APPROVE/CHANGES_REQUESTED, logs to the audit trail |
| `code-reviewer` | General diff review |
| `security-reviewer` | OWASP top 10, authn/authz, RLS policy review, secrets |
| `a11y-reviewer` | WCAG 2.2 AA: contrast, keyboard, focus, semantics, screen reader |

### Skills (`skills/`, shared by both tools)
- **Team/trust (ported from ML playbook, de-ML'd):** `orchestrate-team`, `feature-spec`, `worker-protocol`, `merge-train`, `decision-log`, `pause-and-resume`, `prove-it-works`, `encode-lesson`, `interrogate`, `plan-first`, `tdd-loop`, `verify-before-done`, `systematic-debugging`.
- **Design:** `design-brief` (audience, tone, references loved/hated), `design-tokens` (color/type/spacing/radius/motion as CSS vars + Tailwind theme, light/dark), `component-spec` (variants, states, empty/error/loading), `responsive-layout`, `accessibility-audit`, `visual-review` (screenshot at 375/768/1280, compare to spec), `ux-copy`.
- **Frontend:** `frontend-performance` (Core Web Vitals budgets, image/font loading), `forms-and-validation` (one schema shared client/server).
- **Backend:** `system-design-doc` (template asset), `api-contract` (contract first; generated types), `data-modeling` (Postgres schema, constraints, indexes), `supabase-migrations` (reversible, local only, `db reset` proves it), `rls-policies` (policy per role + pgTAP test per policy), `supabase-auth` (session handling, server vs client clients, never service role in the browser), `edge-functions-vs-rpc` (decision guide), `security-review`, `observability` (errors, logs, health).
- **Quality:** `web-quality-gates` (the gate list below and what each catches).
- Supabase skills are only installed by `init` when the target has a `supabase/` dir (or `--profile supabase`).

### Guardrail hooks (`hooks/guard.py`)
Block: `git push`, `reset --hard`, `supabase link`, `supabase db push`, `supabase functions deploy`, any command with `--db-url`/`--project-ref` to a non-local host, `vercel`/`netlify` deploy. Protect: `.env*`, `supabase/seed` of prod data, `SUPABASE_SERVICE_ROLE_KEY` in client code, gate configs (`configs/gates.json`), visual snapshot baselines, a11y thresholds. Ask before: new dependency, editing an already-applied migration. Auto-format edits (prettier if present).

### Starter app (`templates/web-project/`, rendered by `new`)
Next.js (App Router, TypeScript strict) + Tailwind with tokens in `src/styles/tokens.css` · Supabase local via CLI (`supabase/config.toml`, `migrations/`, `tests/` pgTAP, `seed.sql`) · `@supabase/ssr` server/client helpers · generated `src/lib/database.types.ts` · Zod schemas · one example feature end to end (e.g. auth + a `notes` table with owner-only RLS) · Vitest unit tests · Playwright e2e + `@axe-core/playwright` + screenshot snapshots · ESLint · CI workflow. Package manager: pnpm.

### Gates (`make` targets, same names in both tools' docs)
- `make check` — eslint, `tsc --noEmit`, vitest
- `make db-check` — `supabase db reset` (all migrations apply cleanly from zero) + pgTAP (`supabase test db`) + lint that every public table has RLS enabled + generated types are up to date
- `make ui-check` — Playwright e2e + axe (zero serious/critical) + screenshot diffs at 3 viewports
- `make perf` — Lighthouse CI against budgets in `configs/gates.json` (optional, not in default `check`)

### Codex config
`.codex/config.toml` in the project: `approval_policy`/`sandbox_mode` defaults for workspace-write, network off by default, MCP servers: Supabase MCP (`--read-only`, local), Playwright MCP (screenshots), optional Figma. `AGENTS.md` carries the Code Review Rules (RLS, auth, contract drift, a11y, tokens-not-hex) that `@codex review` applies. Codex has no hooks, so the "needs human approval" list lives in `AGENTS.md`.

### Shared infrastructure (ported and adapted from the ML playbook)
`scripts/playbook.py` (`new` / `init` / `sync`, lockfile, managed vs user files) · `scripts/init.sh` one-line installer · `scripts/check_install_safety.py` · `templates/agent-config/` (AGENTS.md, CLAUDE.md, `tasks/` board, `scripts/agent-team/{run-wave.sh,audit.py,panel_review.py}`, a **pipeline map** reworked to web entry points: pages/routes, server actions/API, DB/RLS, auth, background jobs) · `scripts/skill_eval.py` + `evals/skill-routing.jsonl` · plugin manifests (`.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`) · `docs/` (agent-team, codex, claude-code, design-workflow, backend-architecture, supabase) · tests + CI (CI scaffolds a fresh starter and runs `make check`; `db-check`/`ui-check` run in CI with Supabase CLI + Playwright).

## Decided

- Name `web-agent-playbook`, public, MIT, under `mj2tang` (user).
- Codex **and** Claude Code (user).
- Plug into other projects + starter for new ones (user).
- Backend architecture and design included (user).
- Backend stack: Supabase / PostgreSQL (user).
- `init` links Codex to the web rules by default (user). If `AGENTS.md` exists, append one line, `See AGENTS.web-playbook.md`. If it doesn't, create `AGENTS.md`. `--no-link` opts out. This is the one allowed edit to a user file besides the settings merge, and `check_install_safety.py` allows exactly this line and nothing more.

## Builder's calls (Claude's, reviewable)

- Next.js App Router + TypeScript + Tailwind + pnpm for the starter frontend.
- Playwright + axe + Lighthouse CI for UI gates; pgTAP for DB tests; Vitest for unit.
- Port, rather than share via a library, the team scripts from the ML playbook (copy + adapt; the repos evolve independently).
- Plugin name `web-playbook` (avoids clashing with `agent-playbook` when both are installed).
- Exact skill wording, docs prose, and example feature.
- **Gates in `init` repos:** `init` never edits `package.json` or an existing Makefile. It writes a standalone `scripts/gates/` (`check.sh`, `db-check.sh`, `ui-check.sh`) that discover the project's own lint/typecheck/test scripts from `package.json` and skip gates whose tooling is missing, saying so (`SKIPPED: no playwright config`). Opt-in `--profile supabase` / `--profile ui` adds standalone config files (`playwright.playbook.config.ts`, `supabase/tests/rls_enabled.test.sql`) and **prints** the `pnpm add -D ...` line for the human; it never installs. The starter (`new`) has every gate wired. The supervisor reports skipped gates as findings rather than passes.
- **Codex sandbox:** workers use `workspace-write`, network off, and run `check` only. `db-check` and `ui-check` need Docker, localhost and browsers, so the supervisor runs them through a `[profiles.gates]` profile in `.codex/config.toml` with network on (`codex exec -p gates`), or through Claude Code. `run-wave.sh` with `RUNNER=codex` uses the worker profile. Lessons from the live Codex 0.167 run of the ML playbook (commit `32ac31b`) carry over: Codex's `workspace-write` keeps `.git` read-only, so the runner commits each worker's `owned_files` after it exits and logs any changes outside them. The runner also installs dependencies (`pnpm install --frozen-lockfile`) in each worktree *before* dispatch, with a writable pnpm store. `new` commits the lockfile. The supervisor runs `workspace-write` plus `--add-dir <worktree>`, not `read-only`.
- **Co-installing with the ML playbook:** not supported in v1. `init` detects `.agents/playbook.lock.json` from `coding-agent-playbook` and stops with a message. The web lockfile is `.agents/web-playbook.lock.json`.
- **Settings merge:** same contract as the ML playbook. `.claude/settings.json` may be merged when the result is a strict superset of the original, and `check_install_safety.py` checks that. `.codex/config.toml` is created only if it doesn't exist. If it does, `init` writes `.codex/web-playbook.config.toml` and prints the profile lines for the human to paste.

## Verification of "done"

- `python -m unittest discover -s tests` green (manifests, skills front-matter, hooks block/allow cases, scaffolder new/init/sync, install-safety).
- `playbook.py new /tmp/x --name x` then `make check` green locally; `db-check` and `ui-check` green in CI.
- `check_install_safety.py` passes on a copy of a real Next.js repo.
- `claude plugin validate .` passes.
- Repo created public on GitHub, pushed, CI green.
