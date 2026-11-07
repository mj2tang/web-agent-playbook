# A team of agents for web projects

✅ Works in Claude Code and Codex.

## Topology
```
                 orchestrator (main session)
                 │  plans tasks/, sizes waves by trust, merges
   wave 0 ───────┼──────────────────────────────┐
   system-architect                         ui-designer
   design doc + contract                    brief + tokens + component specs
   (migrations, RLS, pgTAP, types, Zod)
                 │  contract + design merged first
   wave 1..n ────┼──────────────────────────────┐
   backend-worker (worktree)                frontend-worker (worktree)
                 │                               │
                 └──────── supervisor ───────────┘
                   + security-reviewer (auth, RLS, actions)
                   + a11y-reviewer (UI)
                 │  APPROVE → merge-train → main
```

## Why a contract first
Frontend and backend work in parallel only if they agree on shapes. The architect freezes the SQL schema, RLS policies (with pgTAP allow/deny tests), generated database types, and Zod schemas for every boundary. Workers import them and never change them; a needed change goes back to the architect as its own task. `db-check` fails when generated types drift from the migrations.

## Why a designer first
Without a brief and tokens, every worker invents colours and spacing, and the result looks generic. The ui-designer writes a one-page brief from the owner's references (loved and hated), turns it into semantic tokens with light and dark sets, and specifies each component's states before anyone builds it. Workers style only with tokens; the guard and review rules flag raw hex values.

## Lifecycle of a feature
1. `tasks/EPIC.md`: goal, non-goals, a checkable exit condition.
2. Wave 0: architect and designer tasks; merge.
3. Orchestrator writes `T-NNN` task files (`feature-spec`) with disjoint owned files and command-checkable criteria.
4. Workers build in worktrees (`worker-protocol`): test first, gates, commit, prove through the pipeline map.
5. Supervisor re-runs the gates in the worker's checkout, opens the screenshots, checks the proof, and logs a verdict. Security and a11y reviewers join for their areas.
6. `merge-train` lands approved branches one at a time with gates after each merge.

## Trust before parallelism
Workers start at 1 in parallel. `scripts/agent-team/audit.py trust` raises the limit after consecutive clean first-round approvals and lowers it after a revert or human rework. `run-wave.sh` enforces it (`FORCE=1` overrides and is logged). Every decision lands in `.audit/decisions.tsv`. After Lauren Tan's pstack.

## Running it
- Claude Code: `claude --agent orchestrator` → "Build tasks/EPIC.md as a team."
- Codex: `codex` → `$orchestrate-team build tasks/EPIC.md`.
- Headless: `scripts/agent-team/run-wave.sh T-002 T-003` (`RUNNER=codex` for Codex; see [codex.md](codex.md) for the sandbox details).

## Failure modes and fixes
| Symptom | Fix |
|---|---|
| Two workers edit `database.types.ts` or `package.json` | One task owns shared files; others depend on it |
| Worker changes a policy to make its feature work | Contract changes go back to the architect; supervisor flags contract diffs |
| UI passes tests but looks wrong | `visual-review`: open screenshots at 3 widths and both themes against the spec |
| Gate "passes" because the tool isn't installed | Gate scripts exit 4 on skips; SKIPPED is a finding |
| Flaky e2e | Web-first assertions; wait for navigations; never retry into green |
| RLS "works" in testing | Tests ran as `postgres` or the service role; test as `authenticated` with JWT claims |
