# Web Agent Playbook

Set up **web projects for a team of coding agents** — design, Next.js frontend, and Supabase backend — in **Codex** and **Claude Code**. A system architect freezes the data and API contract, a UI designer sets the brief and design tokens, frontend and backend workers build in parallel git worktrees, and a supervisor merges only what passes the gates: lint, types, unit, pgTAP and RLS, axe accessibility, screenshots at three widths.

The web sibling of [coding-agent-playbook](https://github.com/mj2tang/coding-agent-playbook) (ML).

```bash
# Plug the team into an existing web repo (additive; see "What init touches")
curl -fsSL https://raw.githubusercontent.com/mj2tang/web-agent-playbook/main/scripts/init.sh | bash -s -- init .

# Or start a new site: Next.js 16 + Supabase starter, green on first run
curl -fsSL https://raw.githubusercontent.com/mj2tang/web-agent-playbook/main/scripts/init.sh \
  | bash -s -- new my-site --name my-site --bootstrap
cd my-site && make db-start env && make check db-check
make baselines   # first time: writes screenshot baselines - look at them, then commit them
make ui-check
```

Then: `codex` → `$orchestrate-team build tasks/EPIC.md`, or `claude --agent orchestrator` → "Build tasks/EPIC.md as a team."

## What you get

| Layer | Contents |
|---|---|
| **Agent team** | `orchestrator` · `system-architect` (design doc + frozen contract) · `ui-designer` (brief, tokens, component specs) · `frontend-worker` · `backend-worker` (each `isolation: worktree`) · `supervisor` · `security-reviewer` · `a11y-reviewer` · `code-reviewer` |
| **Design skills** | `design-brief`, `design-tokens`, `component-spec`, `responsive-layout`, `accessibility-audit` (WCAG 2.2 AA), `visual-review`, `ux-copy` |
| **Frontend skills** | `frontend-performance` (Core Web Vitals + JS budgets), `forms-and-validation` (one Zod schema client + server) |
| **Backend skills** | `system-design-doc`, `api-contract`, `data-modeling`, `supabase-migrations`, `rls-policies`, `supabase-auth`, `edge-functions-vs-rpc`, `security-review` (OWASP), `observability` |
| **Team and trust skills** | `orchestrate-team`, `feature-spec`, `worker-protocol`, `merge-train`, `decision-log`, `pause-and-resume`, `prove-it-works`, `encode-lesson`, `interrogate` (cross-model review), `plan-first`, `tdd-loop`, `verify-before-done`, `systematic-debugging`, `web-quality-gates` |
| **Gates** | `make check` (ESLint, tsc, Vitest) · `make design-check` (deterministic design lint: tokens, focus, semantics, generic-AI patterns; runs Impeccable's detector too when installed) · `make db-check` (migrations from zero, pgTAP, **RLS on every public table**, type drift) · `make ui-check` (Playwright, axe, screenshots at 375/768/1280 against committed baselines) · `make perf` (Lighthouse). Thresholds live in `configs/gates.json`. In plugged-in repos: `scripts/gates/*.sh`, which use your own `package.json` scripts and report **SKIPPED (exit 4), never a silent pass** |
| **Guardrails** | Guard hook (best-effort command matching, [details](docs/claude-code.md#hooks)) blocks push, deploys, and linked/remote Supabase commands, asking about unknown ones; blocks the service-role key in client code; protects `.env*`, gate budgets, and snapshots; asks before new dependencies, baseline updates, Playwright config edits, and edits to applied migrations |
| **Codex setup** | `AGENTS.md` with Code Review Rules (RLS, authz, secrets, contract drift, a11y, tokens), `.agents/skills/`, the nine roles as native Codex agents (`.codex/agents/*.toml`, generated from `agents/*.md`), the guard as Codex `PreToolUse` hooks (Bash + `apply_patch`), MCP servers in `.codex/config.toml` (local Supabase, Playwright, Figma, Chrome DevTools), and a headless runner with explicit sandbox flags ([details](docs/codex.md)) |
| **Starter** (`new`) | Next.js 16 App Router, TypeScript, Tailwind v4 with design tokens, `@supabase/ssr` auth (sign up/in/out, `src/proxy.ts` session refresh), a `notes` table with owner-only RLS and 8 pgTAP policy tests, Zod contracts, Vitest, Playwright + axe + visual specs, CI |
| **Trust before parallelism** | Workers start at 1 and earn more from clean approvals (`scripts/agent-team/audit.py trust`); every decision lands in `.audit/decisions.tsv`; proof runs through a web **pipeline map** (`routes`, `server-actions-api`, `database-rls`, `auth`, `jobs`) |

## What `init` touches

`init` is additive. It never edits `package.json`, a Makefile, or your source. It installs into new paths (`.agents/`, `.claude/agents/`, `tasks/`, `scripts/agent-team/`, `scripts/gates/`, `docs/pipeline-map/`, `configs/`, `AGENTS.web-playbook.md`), and makes only these edits to existing files:

- **`AGENTS.md`**: appends one line pointing to `AGENTS.web-playbook.md`, because Codex reads only `AGENTS.md` (`--no-link` to skip). If there's no `AGENTS.md`, it creates one with that line.
- **`.claude/settings.json`**: merges in the playbook's script permissions (a strict superset of yours).
- **`.codex/config.toml`**: created only if absent; otherwise the playbook writes `.codex/web-playbook.config.toml` and prints the tables to copy.
- **`CLAUDE.md`**: created only if absent (`@AGENTS.web-playbook.md`); an existing one is left alone, and `init` tells you the line to add.

`python3 scripts/check_install_safety.py . /tmp/scratch ~/my-site` installs into a **copy** of your repo in every mode and fails if anything else changes: a deleted or modified file, a path outside the footprint, git state, or a re-install that isn't a no-op.

| Option | Effect |
|---|---|
| `--profile auto` (default) | `supabase` if `supabase/` exists (Supabase skills + `supabase/tests/rls_enabled.test.sql`); `ui` if a Playwright config exists |
| `--profile ui` | standalone `playwright.playbook.config.ts` + `tests/e2e-playbook/a11y.spec.ts`; prints the `add -D` command, never installs |
| `--guardrails` | guard hook + guarded permissions |
| `--mode plugin` | enable the Claude Code plugin instead of vendoring agents/hooks (skills still copied for Codex) |
| `sync .` | update vendored skills/agents/scripts; keeps files you edited (`--force` to overwrite) |

Installing next to `coding-agent-playbook` in the same repo isn't supported yet; `init` detects it and stops.

## Use it in Codex

1. `init` or `new`, then trust the project and run `codex` **from the project root**. Type `$` or `/skills` to see the skills; name one for fixed workflows, e.g. `$orchestrate-team build tasks/EPIC.md`.
2. **Trust the guard hooks once** (with `--guardrails`, always on for `new`): Codex shows "Hooks need review" at startup, or open `/hooks`. Until you trust them, they don't run - and headless `codex exec` skips untrusted project hooks silently (verified on codex-cli 0.167).
3. **Agents:** the roles are native Codex agents. Codex spawns a custom agent only when asked, so name it: "spawn the `frontend-worker` agent for tasks/T-003-...". The `orchestrate-team` skill does this for you.
4. Headless workers: `RUNNER=codex scripts/agent-team/run-wave.sh T-002 T-003`. Each gets its own worktree, dependencies installed before dispatch, `--sandbox workspace-write` with no network, and the runner commits the worker's owned files (Codex's sandbox keeps `.git` read-only).
5. Supervisor review with the gates (needs Docker/localhost/browsers, so network on):
   ```bash
   codex exec --sandbox workspace-write -c sandbox_workspace_write.network_access=true --add-dir <worktree> \
     "Act as the supervisor defined in .claude/agents/supervisor.md. Review branch task/T-002-<slug> against tasks/T-002-<slug>.md."
   ```
6. `@codex review` on GitHub applies the `## Code Review Rules` in `AGENTS.md`.
7. Guardrails in Codex: the trusted guard hooks, the sandbox, and the "Needs human approval" list in `AGENTS.md`.

## Use it in Claude Code

1. `init` (add `--guardrails` for the guard hook) or `new` (guardrails on). Open `claude` once interactively and trust the folder.
2. `claude --agent orchestrator` → "Build tasks/EPIC.md as a team."
3. Optional: `claude mcp add playwright -- npx -y @playwright/mcp@latest` for interactive screenshots.
4. Plugin only: `/plugin marketplace add mj2tang/web-agent-playbook`, then `/plugin install web-playbook@mj2tang`.

## Pairs well with

This playbook is about the team, the contract, and the gates. For visual taste and specialist guidance, add these (all work in Codex and Claude Code):

| Add | For | Install |
|---|---|---|
| [Impeccable](https://github.com/pbakaus/impeccable) | Auditing and polishing UI against an anti-pattern library; stores your design context | see its README (`/teach-impeccable` once per project) |
| [Anthropic `frontend-design`](https://github.com/anthropics/skills) | Distinctive new pages and components | `npx skills add anthropics/skills --skill frontend-design --agent codex` |
| [Vercel `agent-skills`](https://github.com/vercel-labs/agent-skills) | `web-design-guidelines` (UI audit with `file:line` findings) and `react-best-practices` | `npx skills add vercel-labs/agent-skills` |
| [OpenAI Build Web Apps plugin](https://github.com/openai/plugins) | shadcn/ui, Stripe, Supabase, React best practices, frontend testing | `/plugins` in Codex |
| [shadcn MCP](https://ui.shadcn.com/mcp) | Browse and install registry components | `pnpm dlx shadcn@latest mcp init --client codex` |

Our `design-*` skills set the process (brief → tokens → specs → review); these supply taste and component knowledge. If two skills disagree, the project's `PRODUCT.md`, `DESIGN.md`, and tokens win. Both files use the names Impeccable and gstack read, so they share one design context.

## The 10 rules (web edition)

1. **Write the context file first**: commands, layout, conventions, what's allowed without asking.
2. **Brief and tokens before pixels.** A designer decides the look once; workers don't improvise colours.
3. **Contract before code.** Schema, RLS, types, and Zod schemas frozen before frontend and backend split up.
4. **RLS is the boundary.** On for every table, tested for allow *and* deny, re-checked in every server action.
5. **Give agents a way to check their own work.** Gates they can run in seconds; SKIPPED is not a pass.
6. **Look at the screenshots.** Tests prove behaviour; screenshots at three widths and both themes prove it looks right.
7. **Isolate parallel work.** One worktree and a disjoint set of files per agent.
8. **Separate author and reviewer.** Read-only supervisor, plus security and accessibility reviewers for their areas.
9. **Keep humans on irreversible actions.** Push, deploy, remote Supabase, new dependencies, snapshot updates.
10. **Turn every correction into a check**: a pgTAP test, a Playwright spec, a lint rule, or a hook (`encode-lesson`).

## Guides

| Guide | What's inside |
|---|---|
| [Agent team](docs/agent-team.md) | Topology, contract-first parallelism, trust ladder, failure modes |
| [Design workflow](docs/design-workflow.md) | Brief → tokens → specs → build → responsive, a11y, visual, performance checks |
| [Backend architecture](docs/backend-architecture.md) | Design doc, where logic runs, two-layer authorization, observability |
| [Supabase](docs/supabase.md) | Local-only workflow, the RLS gate, CLI 3.0 notes, port conflicts |
| [Codex](docs/codex.md) | AGENTS.md, skills, sandbox flags verified on 0.167, headless runs, MCP |
| [Claude Code](docs/claude-code.md) | Subagents, skills, hooks, permissions, plugins |
| [Skill routing evals](evals/) | One routing case per skill plus near-miss negatives |
| [Resources](resources.md) | Links |

## Repository layout

```
.claude-plugin/ .codex-plugin/ .agents/plugins/   plugin + marketplace manifests
skills/                  Agent Skills (shared by Claude Code and Codex)
agents/                  Subagent definitions
hooks/                   hooks.json + guard.py
templates/web-project/   Next.js + Supabase starter (rendered by `new`)
templates/agent-config/  AGENTS.md, CLAUDE.md, task board, pipeline map, gate scripts, team scripts, Codex config
templates/profiles/      opt-in files for `init --profile supabase|ui`
scripts/                 playbook.py · init.sh · check_install_safety.py · skill_eval.py
tests/  evals/  docs/
```

## Develop

```bash
uv run --python 3.12 --no-project python -m unittest discover -s tests -v
claude plugin validate .
```
CI also scaffolds the starter and runs `make check db-check ui-check` against a real local Supabase.

## Contributing

Skills should be specific and tested, with descriptions that say when **and when not** to use them. Add a routing case to `evals/skill-routing.jsonl` for every new skill. Date anything version-specific.

MIT licensed.
