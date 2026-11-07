# {{project}}

{{description}}

Next.js (App Router) + Supabase (Postgres, Auth, RLS), set up for a team of coding agents by
[web-agent-playbook](https://github.com/mj2tang/web-agent-playbook).

## Run it
```bash
pnpm install
make db-start            # local Supabase in Docker
make env                 # writes .env.local from the local stack
pnpm dev                 # http://localhost:3000
```

First time only: `make baselines` writes the screenshot baselines; look at them in `tests/e2e/*-snapshots/` and
commit them. `make ui-check` fails while baselines are missing, so screenshots are always compared. Linux baselines
for CI come from the CI `baselines` artifact.

Another local Supabase project already running? Stop it (`supabase stop` in that project) or change the ports in
`supabase/config.toml` (`[api]`, `[db]`, `[studio]`, ...). `make env` reads whatever the local stack reports.

## Gates
| Command | What it checks |
|---|---|
| `make check` | ESLint, TypeScript, Vitest |
| `make db-check` | migrations apply from zero, pgTAP (RLS on every table, notes policies), generated types up to date |
| `make ui-check` | Playwright journeys, axe (no serious/critical issues), screenshots at 375/768/1280 |
| `make perf` | Lighthouse budgets |

## Agent team
- Claude Code: `claude --agent orchestrator` → "Build tasks/EPIC.md as a team."
- Codex: `codex` → `$orchestrate-team build tasks/EPIC.md`; headless workers: `RUNNER=codex scripts/agent-team/run-wave.sh T-001`.

Rules, approvals, and review rules live in `AGENTS.md`.
