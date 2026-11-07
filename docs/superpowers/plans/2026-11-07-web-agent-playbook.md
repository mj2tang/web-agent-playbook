# web-agent-playbook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public repo, `mj2tang/web-agent-playbook`, that plugs a Codex and Claude Code agent team into web projects (design, Next.js frontend, Supabase backend), or scaffolds a Supabase starter app that is green on first run.

**Architecture:** Same shape as `mj2tang/coding-agent-playbook`, which is the *sibling* below: shared `skills/` and `agents/`, a Python-stdlib scaffolder (`scripts/playbook.py new|init|sync`) that renders `templates/`, and a guard hook. Team scripts are copied from the sibling and adapted, not imported. Every web-specific behaviour is new content.

**Tech Stack:**
- Playbook: Python 3.12 stdlib (scaffolder, hook, tests via `unittest`), bash.
- Starter app: Next.js 15 App Router, TypeScript strict, Tailwind v4, pnpm, `@supabase/ssr`, Supabase CLI (as the npm devDependency `supabase`), pgTAP, Zod, Vitest, Playwright, `@axe-core/playwright`.

**Spec:** `docs/superpowers/specs/2026-11-07-web-agent-playbook-design.md`

**Sibling (read-only reference):** clone `mj2tang/coding-agent-playbook` at `32ac31b` or later into the scratchpad. Paths written `sibling:<path>` refer to it.

## Global Constraints

- Repo is `mj2tang/web-agent-playbook`, public, MIT. Plugin name `web-playbook`, marketplace `mj2tang`, version `0.1.0` in both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`.
- Lockfile path is `.agents/web-playbook.lock.json`. Instructions file for existing repos is `AGENTS.web-playbook.md`.
- `init` never edits `package.json`, an existing Makefile, or source. It may only:
  - merge `.claude/settings.json` (strict superset of the original),
  - append the single line `See AGENTS.web-playbook.md for the web agent team's rules, gates, and approvals; read it before any task.` to an existing `AGENTS.md`, unless `--no-link` is given.
  
  It never edits an existing `.codex/config.toml`. In that case it writes `.codex/web-playbook.config.toml` instead.
- `init` stops with exit 1 if `.agents/playbook.lock.json` (the ML playbook) exists.
- No ML content anywhere. CI fails on these words in `skills/`, `agents/` and `templates/`: `mlflow|leakage|rebaseline|champion|databricks|uv sync`.
- Every skill description contains `Use ` and `Not `, and is under 1024 characters. Every agent's `skills:` list names existing skills.
- Gate names everywhere: `make check`, `make db-check`, `make ui-check`, `make perf`. In `init` repos the same gates run as `scripts/gates/check.sh|db-check.sh|ui-check.sh`.
- Agents work only against the local Supabase. Remote, link, deploy and service-role actions are blocked or need a human.
- Run tests with `uv run --python 3.12 --no-project python -m unittest discover -s tests` (system python3 + pytest fails on collection).
- Every commit ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **`AGENTS.md` without a trailing newline, or with CRLF line endings, and `init` run twice.** Expect exactly one pointer line appended once, the original bytes kept as a prefix, and the second run a no-op. Test in Task 6.
2. **A repo using npm or yarn, or with no `lint`/`typecheck`/`test` scripts in `package.json`.** Expect the gate scripts to use the repo's package manager (from its lockfile) and print `SKIPPED: <gate> (<reason>)`, not pass silently. The supervisor counts SKIPPED as a finding. Test in Task 5.
3. **Remote Supabase reached through a wrapper or an alias**, such as `pnpm exec supabase db push`, `npx supabase link --project-ref x`, `psql postgresql://…supabase.co`, or `supabase db push --db-url …`. Expect a block. `supabase db push --local` and `supabase db reset` stay allowed. Test in Task 4.
4. **A migration that creates a public table without RLS, or runs `alter table … disable row level security`.** Expect `make db-check` to fail and name the table. Test in Task 8 (pgTAP `rls_enabled.test.sql`).
5. **`sync` after a user edited a vendored skill, and after the user deleted one.** Expect the edit to be kept (reported as skipped), and the deleted file not to be recreated silently: it is reported as `created`, because it's managed and absent. Test in Task 6.

---

### Task 1: Repo skeleton and packaging

**Files:**
- Create: `LICENSE` (MIT, "Eric Tang"), `.gitignore`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `hooks/hooks.json`
- Test: `tests/test_packaging.py`

**Interfaces:**
- Produces: `tests/helpers.py` with `ROOT: Path`, `frontmatter(path: Path) -> dict[str, str]`, and `run_playbook(*args, cwd=None) -> str` (subprocess, `check=True`, returns stdout). Later tests import these.

- [ ] **Step 1:** `git init -b main` in `scratchpad/web-agent-playbook` (the spec and this plan are already there).
- [ ] **Step 2: Write failing tests** in `tests/test_packaging.py`:
  - `test_manifests_valid_and_versions_match`: all 5 JSON files parse, the Claude and Codex versions are both `"0.1.0"`, and `name == "web-playbook"`.
  - `test_skills_frontmatter`: for each `skills/*/SKILL.md`, `name` equals its directory, and the description contains `Use ` and `Not ` and is under 1024 characters. `len(skills) >= 30` is added in Task 3; for now assert `>= 0`.
  - `test_agents_reference_existing_skills`: same check as `sibling:tests/test_playbook.py::test_agents_reference_existing_skills`.
  - `test_no_ml_content`: grep the regex from Global Constraints across `skills/`, `agents/` and `templates/`, case-insensitive, with zero hits.
- [ ] **Step 3:** Run the tests and expect FAIL (missing manifests).
- [ ] **Step 4:** Write the manifests, modelled on the sibling's (same shape and keys). Descriptions are web-specific, and the Codex `interface.displayName` is `"Web Agent Playbook"`. `hooks/hooks.json` is the sibling's file unchanged.
- [ ] **Step 5:** Run the tests and expect PASS. Commit `Skeleton: manifests, license, packaging tests`.

### Task 2: Ported team and trust skills

**Files:**
- Create: `skills/{orchestrate-team,feature-spec,worker-protocol,merge-train,decision-log,pause-and-resume,prove-it-works,encode-lesson,interrogate,plan-first,tdd-loop,verify-before-done,systematic-debugging}/SKILL.md`

**Interfaces:**
- Produces: the skill names above, which agents (Task 4) preload.

- [ ] **Step 1:** Copy each skill from the sibling, then rewrite its ML specifics for web:
  - `make gate`/`data-check` become `make check`/`db-check`/`ui-check`.
  - Pipeline-map entry points become `routes`, `server-actions-api`, `database-rls`, `auth`, `jobs`.
  - Evidence is a screenshot path, Playwright report, pgTAP output, or `curl` against `localhost`, each with `git_sha`.
  
  `worker-protocol` keeps the Codex note from sibling `32ac31b`: don't commit in the Codex sandbox, because the runner commits your owned files.
- [ ] **Step 2:** Run `test_skills_frontmatter` and `test_no_ml_content`. Expect PASS. Commit `Team and trust skills (ported, web edition)`.

### Task 3: Design, frontend, backend and quality skills

**Files:**
- Create: `skills/{design-brief,design-tokens,component-spec,responsive-layout,accessibility-audit,visual-review,ux-copy,frontend-performance,forms-and-validation,system-design-doc,api-contract,data-modeling,supabase-migrations,rls-policies,supabase-auth,edge-functions-vs-rpc,security-review,observability,web-quality-gates}/SKILL.md`
- Create: `skills/system-design-doc/assets/system-design-template.md`, `skills/design-brief/assets/design-brief-template.md`
- Modify: `tests/test_packaging.py` (raise the count to `>= 32`)

**Interfaces:**
- Produces: `SUPABASE_SKILLS = {"supabase-migrations", "rls-policies", "supabase-auth", "edge-functions-vs-rpc"}`. The scaffolder (Task 6) installs these only when the target has `supabase/` or uses `--profile supabase`. The constant lives in `scripts/playbook.py`; tests read it from there.

Content each skill must carry (one numbered procedure plus a "Done when" line that can be checked with a command):
- `design-tokens`: tokens live in `src/styles/tokens.css` as CSS custom properties: `--color-*` (semantic: `bg`, `fg`, `muted`, `accent`, `danger`, `border`), `--font-*`, `--space-*` (4px scale), `--radius-*`, `--shadow-*` and `--duration-*`. There are light and dark sets (`prefers-color-scheme` plus `[data-theme]`) and a Tailwind `@theme` mapping. Rule: no raw hex or px in components. Also an "avoid generic AI look" checklist: no default purple gradients, one typeface pair chosen from the brief, real copy.
- `visual-review`: screenshots at 375, 768 and 1280 widths using Playwright MCP or `pnpm exec playwright test --grep @visual`, compared to `component-spec`. Covers states (hover, focus, empty, error, loading) and dark mode.
- `accessibility-audit`: WCAG 2.2 AA. axe must have zero `serious` or `critical` violations. Keyboard-only path, visible focus, 24×24 minimum targets, contrast of 4.5:1 for text and 3:1 for UI.
- `frontend-performance`: budgets are LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms, and JS ≤ 170KB gzip per route. Covers `next/image`, `next/font`, and server components by default.
- `rls-policies`: enable RLS on every table in `public`. Each policy is written per role (`anon`, `authenticated`) and per operation, using `(select auth.uid())`. Each policy needs a pgTAP test that proves both allow and deny.
- `supabase-migrations`: `supabase migration new <name>`, never edit an applied migration, prove it with `supabase db reset`, regenerate types with `supabase gen types typescript --local > src/lib/database.types.ts`. Local only.
- `supabase-auth`: use `createServerClient` in server code and `createBrowserClient` in the browser, refresh sessions in middleware, never expose `SUPABASE_SERVICE_ROLE_KEY` to code under `src/app/**` client components, and use `auth.getUser()` (not `getSession()`) for authorisation.
- `api-contract`: the contract is three things — the SQL schema, the RLS policies, and Zod schemas in `src/lib/contracts/`, all frozen by the architect. Workers may not change it. A change goes back to the `system-architect`.
- `edge-functions-vs-rpc`: a decision table. Postgres function/RPC for data-local logic under RLS; server action for form mutations; route handler for webhooks; Edge Function for third-party secrets or work outside the request.
- `security-review`: OWASP Top 10 mapped to Next.js and Supabase. Covers authz on every server action, input validation with Zod, no secrets in `NEXT_PUBLIC_*`, CSRF via server actions, and SSRF in fetch-by-URL.
- Each of the remaining skills (`design-brief`, `component-spec`, `responsive-layout`, `ux-copy`, `forms-and-validation`, `system-design-doc`, `data-modeling`, `observability`, `web-quality-gates`) has a procedure and template matching its name in the spec. `web-quality-gates` lists each gate, what it catches, and states that **SKIPPED is not a pass**.

- [ ] **Step 1:** Write the skills.
- [ ] **Step 2:** Run the packaging tests and expect PASS. Commit `Design, frontend, backend, and quality skills`.

### Task 4: Agents and guard hook

**Files:**
- Create: `agents/{orchestrator,system-architect,ui-designer,frontend-worker,backend-worker,supervisor,code-reviewer,security-reviewer,a11y-reviewer}.md`
- Create: `hooks/scripts/guard.py`
- Test: `tests/test_guard.py`

**Interfaces:**
- Consumes: skill names from Tasks 2 and 3.
- Produces: `guard.py` CLI with modes `bash|files|format`, the sibling's protocol: exit 2 to block, a JSON `ask` decision on stdout, `PLAYBOOK_GUARD_OFF=1` to bypass.

- [ ] **Step 1: Agents.** Same frontmatter as the sibling (`name`, `description`, `tools`, `model`, `skills`, and `isolation: worktree` for the workers).
  - `supervisor`: read-only tools. It runs the gates in the worker's worktree. Its output block is `VERDICT / GATES: check= db-check= ui-check= / SKIPPED: / FINDINGS:`, and it logs with `audit.py log review`.
  - `system-architect`, `ui-designer`, and the reviewers: no Edit tool on `src/`. The architect may write `docs/design/` and `supabase/migrations/` **only** while the contract is being frozen, before workers start.
- [ ] **Step 2: Write failing tests** in `tests/test_guard.py`:
  - `test_blocks`: each of these exits 2.
    - `git push origin main`
    - `git -C ../wt push`
    - `git reset --hard HEAD~1`
    - `supabase link --project-ref abc`
    - `pnpm exec supabase db push`
    - `npx supabase db push --linked`
    - `supabase db push --db-url postgresql://u@db.x.supabase.co/postgres`
    - `supabase functions deploy hello`
    - `psql postgresql://u@db.abc.supabase.co:5432/postgres`
    - `vercel --prod`
    - `netlify deploy --prod`
    - `rm -rf ~`
  - `test_asks`: each of these returns `"ask"`.
    - `pnpm add zod`
    - `npm install lodash`
    - `yarn add x`
    - `pnpm exec playwright test --update-snapshots`
    - `supabase migration repair 2024`
  - `test_allows`: each of these exits 0 with no ask.
    - `pnpm install --frozen-lockfile`
    - `supabase db reset`
    - `pnpm exec supabase db push --local`
    - `supabase start`
    - `supabase test db`
    - `make db-check`
    - `git commit -m 'T-1: x'`
    - `psql postgresql://postgres:postgres@127.0.0.1:54322/postgres`
  - `test_protects_paths`: each of these exits 2.
    - `/p/.env.local`
    - `/p/configs/gates.json`
    - `/p/tests/e2e/__screenshots__/home.png`
    - `/p/tests/e2e/home.spec.ts-snapshots/x.png`
    - `/p/supabase/.temp/project-ref`
    
    `/p/src/app/page.tsx` exits 0.
  - `test_blocks_service_role_in_client_code`: a `files` event writing `/p/src/app/x/page.tsx` with `content` containing `SUPABASE_SERVICE_ROLE_KEY` or `service_role` and `"use client"` exits 2. The same content in `/p/src/lib/server/admin.ts` exits 0.
  - `test_asks_before_editing_applied_migration`: for an `Edit` of `supabase/migrations/<f>.sql` where `<f>` is tracked in git (fixture: a temporary repo with a committed migration, `cwd` set via `event["cwd"]`), return `ask`. A new untracked migration file exits 0.
- [ ] **Step 3:** Run and expect FAIL.
- [ ] **Step 4:** Implement `guard.py` starting from the sibling's.
  - Keep `GIT` and `rm`.
  - Remote-Supabase detection: `supabase\s+(link|db\s+push(?![^\n]*--local)|functions\s+deploy|secrets\s+set)` and any `postgres(ql)?://` whose host is not `127.0.0.1|localhost|0.0.0.0`.
  - Dependency asks for `pnpm|npm|yarn|bun` `add|install <pkg>`. A bare `install` or `--frozen-lockfile` is allowed.
  - The `files` mode reads `tool_input.content`/`new_string` for the service-role check.
  - Applied-migration check: `git -C <cwd> ls-files --error-unmatch <path>`.
  - Format with prettier only when `node_modules/.bin/prettier` exists in `cwd`.
- [ ] **Step 5:** Run and expect PASS. Commit `Agents and guard hook`.

### Task 5: Agent-config templates and gate scripts

**Files:**
- Create: `templates/agent-config/AGENTS.md`, `templates/agent-config/CLAUDE.md` (`@AGENTS.md`), `templates/agent-config/tasks/{BOARD.md,EPIC.md,_TEMPLATE.md}`, `templates/agent-config/docs/pipeline-map/{README,routes,server-actions-api,database-rls,auth,jobs}.md`
- Create: `templates/agent-config/scripts/agent-team/{run-wave.sh,audit.py,panel_review.py}`, copied from the sibling at `32ac31b`
- Create: `templates/agent-config/scripts/gates/{lib.sh,check.sh,db-check.sh,ui-check.sh}`
- Create: `templates/agent-config/.codex/config.toml`, `templates/agent-config/configs/{team.json,gates.json}`
- Test: `tests/test_gates.py`, `tests/test_team_scripts.py`

**Interfaces:**
- Produces:
  - `scripts/gates/lib.sh` defines `pm` (prints `pnpm|npm|yarn|bun` from the lockfile, default `npm`), `has_script <name>` (returns 0 when `package.json` has `scripts.<name>`), and `skip "<gate>" "<reason>"`, which prints `SKIPPED: <gate> (<reason>)` and sets the exit code 0 only when `GATES_ALLOW_SKIP=1`. Otherwise a skip exits 4, so a skip never looks like a pass.
  - `check.sh` runs `lint`, `typecheck` (or `tsc --noEmit` when `tsconfig.json` exists) and `test`.
  - `db-check.sh` runs `supabase db reset`, then `supabase test db`, then type-drift. It's skipped when there is no `supabase/` directory.
  - `ui-check.sh` runs `playwright test` with `playwright.playbook.config.ts` when present, otherwise the repo's own config. It's skipped when there is neither.
- Produces: `.codex/config.toml` with these tables:
  - top level: `sandbox_mode = "workspace-write"`, `approval_policy = "on-request"`
  - `[sandbox_workspace_write] network_access = false`
  - `[profiles.worker]` (the same settings)
  - `[profiles.gates]`: `[profiles.gates.sandbox_workspace_write] network_access = true`
  - `[mcp_servers.supabase]`: `command = "npx"`, `args = ["-y", "@supabase/mcp-server-supabase@latest", "--read-only"]`, local URL via env
  - `[mcp_servers.playwright]`: `npx @playwright/mcp@latest`

  Before writing the profile and network keys, check them against Codex 0.167: run `codex exec -p gates --help` and read `codex --help`. The same check confirms the `-p` flag.
- Produces: `run-wave.sh`, the sibling's script with these changes:
  - Before dispatch it runs `pnpm install --frozen-lockfile` (`$(pm)` equivalent) in each worktree instead of `uv sync`, and adds `--add-dir "$(pnpm store path)"` to the Codex arguments.
  - The worker prompt says the gate is `make check` or `scripts/gates/check.sh`.
  - Codex runs with `-p worker`.
  - The ug runners are removed.

Steps:
- [ ] **Step 1: Write failing tests** in `tests/test_gates.py`. Each one uses a temporary directory, a fake `package.json`, and fake binaries on `PATH` that print their argv.
  - `test_pm_detection`: `pnpm-lock.yaml` → `pnpm`, `package-lock.json` → `npm`, `yarn.lock` → `yarn`, none → `npm`.
  - `test_check_runs_repo_scripts`: with `lint`, `typecheck` and `test` scripts present, the fake `pnpm` receives `run lint`, `run typecheck` and `run test`, and the exit code is 0.
  - `test_missing_script_is_skipped_not_passed`: with no `lint` script, the output contains `SKIPPED: lint (no "lint" script in package.json)` and the exit code is 4. With `GATES_ALLOW_SKIP=1`, the exit code is 0.
  - `test_db_check_skipped_without_supabase`.
- [ ] **Step 2:** Write `tests/test_team_scripts.py`. Port `sibling:tests/test_audit.py` unchanged for `audit.py`. Port the fake-`codex` commit test from `32ac31b`, with these assertions changed: a fake `pnpm` records `install --frozen-lockfile`, and the Codex argv contains `-p worker`.
- [ ] **Step 3:** Run and expect FAIL.
- [ ] **Step 4:** Implement the templates and scripts. `AGENTS.md` sections are the same as the sibling's:
  - Commands, Layout, Conventions (tokens not hex, server components by default, Zod at boundaries, RLS on every table)
  - Allowed without asking
  - Needs human approval (push, deploy, any remote Supabase command, service-role key, adding a dependency, editing an applied migration, snapshot updates, `configs/gates.json`)
  - Proof and trail
  - Agent team (the architect freezes the contract first)
  - Code Review Rules: RLS, authz in server actions, contract drift, a11y, tokens, secrets, type drift
- [ ] **Step 5:** Run and expect PASS. Commit `Agent-config templates, gate scripts, codex config, team scripts`.

### Task 6: Scaffolder `init` and `sync`

**Files:**
- Create: `scripts/playbook.py`, `scripts/init.sh`, both adapted from the sibling
- Test: `tests/test_scaffolder.py`

**Interfaces:**
- Consumes: everything under `skills/`, `agents/` and `templates/agent-config/`, plus `SUPABASE_SKILLS`.
- Produces:
  - CLI `playbook.py init <dir> [--mode vendor|plugin] [--profile auto|core|supabase|ui|full] [--guardrails] [--no-link] [--force] [--dry-run]`. `auto`, the default, means `supabase` if the target has `supabase/`, plus `ui` if it has a Playwright config.
  - CLI `playbook.py sync <dir> [--force]`.
  - `install_agent_setup(s, mode, *, profile, guardrails, existing_repo, link)`, which Task 8's `new` reuses.

Steps:
- [ ] **Step 1: Write failing tests**, porting the sibling's `TestScaffolder` init/sync tests with the names changed, plus:
  - `test_init_appends_pointer_once`: `AGENTS.md` is `"# mine"` (no newline). After `init` it is `"# mine\n\n" + POINTER + "\n"`. A second `init` leaves the bytes unchanged.
  - `test_init_crlf_agents_md`: `"# mine\r\n"` keeps the CRLF prefix byte for byte and gets exactly one pointer line.
  - `test_init_no_link`: `AGENTS.md` is unchanged.
  - `test_init_creates_agents_md_when_absent`: the new `AGENTS.md` contains the pointer line only. `CLAUDE.md` is created only if absent, containing `@AGENTS.web-playbook.md`.
  - `test_init_refuses_alongside_ml_playbook`: with `.agents/playbook.lock.json` present, the exit code is 1 and the message mentions `coding-agent-playbook`.
  - `test_init_codex_config_sidecar`: an existing `.codex/config.toml` is unchanged, `.codex/web-playbook.config.toml` is written, and stdout contains `[profiles.gates]`.
  - `test_profile_auto_supabase`: with `supabase/` present, `.agents/skills/rls-policies` exists. Without it, it doesn't.
  - `test_init_never_touches_package_json`: `package.json` bytes are unchanged, and stdout contains `pnpm add -D` when `--profile ui` is given.
  - `test_sync_keeps_edits_and_restores_deleted`: covers Review Focus #5.
- [ ] **Step 2:** Run and expect FAIL.
- [ ] **Step 3:** Implement, adapting the sibling's `Scaffolder` class unchanged except for these:
  - `LOCK`, `PLUGIN` and `PLUGIN_REPO` take the new names.
  - `append_line` detects `\r\n` in the existing text and uses it.
  - `write_if_absent_else_sidecar(rel, sidecar_rel, content)` is new.
  - The permission tiers are web versions: `make check|db-check|ui-check|perf`, `scripts/gates/*`, `pnpm run *`, `pnpm exec playwright test`, `supabase start|stop|status|db reset|test db|gen types --local|migration new`, and the git rules unchanged from the sibling.
- [ ] **Step 4:** Run and expect PASS. Commit `Scaffolder init/sync`.

### Task 7: Install-safety check

**Files:**
- Create: `scripts/check_install_safety.py`, adapted from the sibling
- Test: `tests/test_install_safety.py`

- [ ] **Step 1: Write a failing test.** Build a fixture repo: `package.json`, `pnpm-lock.yaml`, `AGENTS.md`, `.claude/settings.json`, `.codex/config.toml`, a `supabase/` directory, one committed file and one uncommitted change. Run the checker in vendor and plugin modes and expect exit 0. Then patch the playbook copy so `init` also writes a second line to `AGENTS.md`, and expect exit 1 with `AGENTS.md` in the output.
- [ ] **Step 2:** Implement. Update `FOOTPRINT` to the new paths, including `scripts/gates/`, `.codex/web-playbook.config.toml` and `.codex/config.toml` when it was new. The only allowed `AGENTS.md` change is: `new == old + sep + POINTER + eol`.
- [ ] **Step 3:** Run and expect PASS. Commit.

### Task 8: Starter app and `new`

**Files:**
- Create: `templates/web-project/` containing:
  - `package.json` with scripts `dev`, `build`, `lint`, `typecheck`, `test`, `test:e2e`, `db:types`, `db:types:check`
  - `next.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `postcss.config.mjs`, `vitest.config.ts`, `playwright.config.ts`, `Makefile`, `.env.example`, `.gitignore`, `README.md`
  - `src/styles/tokens.css`, `src/app/{layout.tsx,page.tsx,globals.css}`, `src/app/login/page.tsx`, `src/app/notes/{page.tsx,actions.ts}`
  - `src/lib/supabase/{server.ts,client.ts,middleware.ts}`, `src/middleware.ts`, `src/lib/contracts/notes.ts`, `src/lib/database.types.ts`
  - `supabase/config.toml`, `supabase/migrations/20261107000000_notes.sql`, `supabase/seed.sql`, `supabase/tests/{rls_enabled.test.sql,notes_rls.test.sql}`
  - `tests/unit/contracts.test.ts`, `tests/e2e/{home.spec.ts,a11y.spec.ts,visual.spec.ts}`
  - `.github/workflows/ci.yml`
- Modify: `scripts/playbook.py` (add the `new` command)
- Test: `tests/test_scaffolder.py::test_new_layout`, plus the real runs below

**Interfaces:**
- Consumes: `install_agent_setup(..., existing_repo=False, profile="full", guardrails=True)`.
- Produces: `make check|db-check|ui-check|perf`, where `db-check` runs `pnpm exec supabase db reset && pnpm exec supabase test db && pnpm run db:types:check`.

Fixed content:
- Migration: `public.notes(id uuid pk default gen_random_uuid(), owner uuid not null references auth.users default auth.uid(), body text not null check (length(body) between 1 and 2000), created_at timestamptz not null default now())`, then `enable row level security`, then four policies (select, insert, update, delete), each `to authenticated using/with check ((select auth.uid()) = owner)`.
- `rls_enabled.test.sql`: one pgTAP assertion that `select count(*) from pg_tables where schemaname='public' and not rowsecurity` is `0`. On failure it lists the table names.
- `notes_rls.test.sql`: user A can't select, update or delete user B's note, and `anon` can't select any note. Use `set local role authenticated` and `set local request.jwt.claims`.
- The e2e home spec doesn't need auth. `a11y.spec.ts` runs `AxeBuilder` on `/` and `/login` and filters `serious` and `critical` impacts to `[]`. `visual.spec.ts` is tagged `@visual` and takes three viewport projects.

Steps:
- [ ] **Step 1:** Write a failing `test_new_layout`. Check that the key paths exist, that `AGENTS.md` and `package.json` contain no `{{`, that the `name` in `package.json` equals `--name`, and that `git log` has `Scaffold`.
- [ ] **Step 2:** Implement the template and `cmd_new`. `--bootstrap` runs `pnpm install`, then `make check`, then commits `pnpm-lock.yaml` (lesson from sibling `32ac31b`).
- [ ] **Step 3:** Run the unit tests and expect PASS.
- [ ] **Step 4: Real run.** Run `playbook.py new $SCRATCH/demo --name demo --bootstrap`, then `make -C $SCRATCH/demo check db-check`. Docker is running locally, and the Supabase CLI comes in through the devDependency. Then `pnpm exec playwright install chromium && make ui-check`. All three must be green.
- [ ] **Step 5: Negative proof for Review Focus #4.** Add a migration with `create table public.leaky(id int)`, run `make db-check`, and expect a FAIL naming `leaky`. Then remove the migration.
- [ ] **Step 6:** Commit `Starter app (Next.js + Supabase) and new command`.

### Task 9: Docs, evals, skill-eval, CI

**Files:**
- Create: `README.md` (same structure as the sibling's: what you get, install options, Codex section first, Claude Code, the 10 rules web edition, guides, layout, develop)
- Create: `docs/{agent-team,codex,claude-code,design-workflow,backend-architecture,supabase}.md`
- Create: `resources.md`, `evals/README.md`, `evals/skill-routing.jsonl` (one case per skill, at least 32 lines)
- Create: `scripts/skill_eval.py`, `.claude/skills/skill-eval/SKILL.md` (ported)
- Create: `.github/workflows/ci.yml`
- Test: `tests/test_evals.py`

- [ ] **Step 1: Failing test.** Every skill directory appears as `expected_skill` in at least one `evals/skill-routing.jsonl` line, and every line parses.
- [ ] **Step 2:** Write the docs and evals. `docs/codex.md` documents:
  - the read-only `.git` sandbox and the runner committing
  - `-p worker` and `-p gates`
  - the supervisor command `codex exec -p gates --sandbox workspace-write --add-dir <worktree> "Act as the supervisor defined in .claude/agents/supervisor.md …"`
- [ ] **Step 3:** Write CI with two jobs:
  - `playbook`: Python 3.12, run the unittests.
  - `starter`: `pnpm/action-setup`, Node 22, `supabase/setup-cli`, `playbook.py new /tmp/demo --name demo --bootstrap`, `pnpm exec playwright install --with-deps chromium`, `make -C /tmp/demo check db-check ui-check`.
- [ ] **Step 4:** Run the full test suite and `claude plugin validate .`, and expect PASS. Commit.

### Task 10: Publish

- [ ] **Step 1:** Run `check_install_safety.py` on a copy of a real Next.js repo. Generate one with `pnpm create next-app@latest $SCRATCH/realnext --ts --app --tailwind --eslint --use-pnpm --no-src-dir --yes` and commit it. Expect PASS.
- [ ] **Step 2:** `gh repo create mj2tang/web-agent-playbook --public --source . --description "Codex + Claude Code agent team for designing and building websites: design, Next.js frontend, Supabase backend" --push`.
- [ ] **Step 3:** `gh run watch --exit-status` until both jobs are green. Fix and push until they pass.
- [ ] **Step 4:** Update the memory note `web-agent-playbook.md`: the repo URL, the state, and that CI is green.
