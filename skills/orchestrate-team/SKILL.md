---
name: orchestrate-team
description: Run a team of coding agents on a web project - have the system-architect freeze the API/data contract and the ui-designer the design tokens first, decompose the goal into parallel frontend/backend tasks, dispatch workers in isolated git worktrees within the parallelism the team has earned (trust ladder), route each result through the supervisor, merge only proven and gated work, and drive autonomous runs to a checkable exit condition. Use when asked to build several features at once, run an epic, or work "as a team". Not for a single small change - just do it directly.
---

# Orchestrate a team of agents

Throughput comes from trust, not from the number of agents. Earn trust in one worker's output through verification, then widen the wave.

## Roles
| Role | Runs as | Writes code? | Owns |
|---|---|---|---|
| Orchestrator | main session (`claude --agent orchestrator`) | rarely | `tasks/`, integration, merges, the decision trail |
| System architect | subagent, before wave 1 | contract only | `docs/design/system.md`, `supabase/migrations/` (contract), `src/lib/contracts/` |
| UI designer | subagent, before wave 1 | tokens/specs only | `PRODUCT.md`, `DESIGN.md`, `src/styles/tokens.css`, `docs/design/components/` |
| Frontend / backend workers | subagents, `isolation: worktree` | yes | the files listed in their task |
| Supervisor (+ security, a11y reviewers) | subagents, read-only | no | verdicts |

## Procedure
1. **Load state:** `AGENTS.md` (or `AGENTS.web-playbook.md`), `tasks/BOARD.md`, every `tasks/T-*.md`, `configs/team.json`, `configs/gates.json`, `docs/pipeline-map/README.md`. If `tasks/RESUME.md` exists, follow `pause-and-resume` (Resume) first.
2. **Set the exit condition** for the run as a checkable predicate before dispatching anything, e.g. "T-001..T-004 merged and `make check db-check ui-check` passes on main". Write it in `tasks/EPIC.md` and log it (`decision-log`, phase `plan`).
3. **Freeze the contract (wave 0).** If the epic changes data or APIs, run `system-architect` (`system-design-doc`, `api-contract`, `data-modeling`, `rls-policies`). If it changes UI, run `ui-designer` (`design-brief`, `design-tokens`, `component-spec`). Merge their work first. Workers build *against* it and never change it.
4. **Plan:** write/refresh task files with `feature-spec`. A "wave" = `todo` tasks whose dependencies are `done` and whose owned files don't overlap. Frontend and backend tasks for the same feature can run in parallel once the contract is frozen.
5. **Size the wave by trust:** `python3 scripts/agent-team/audit.py trust` prints how many workers the team has earned (starts at 1; rises after clean approvals; drops after a revert or human rework). Never dispatch more. `--explain` shows why.
6. **Dispatch:** for each task in the wave, mark `in_progress`, log a `dispatch` row, and launch the matching worker in the background (Claude Code: the subagent; Codex: spawn the custom agent **by name**, e.g. `frontend-worker` - Codex never spawns custom agents unless asked) with:
   > Task file: `tasks/T-012-<slug>.md`. Branch: `task/T-012-<slug>`. Follow worker-protocol and prove-it-works. Return the summary block only.
7. **Collect:** as each worker returns, check its EVIDENCE line exists, set `review`, and launch the `supervisor` on its branch. Add `security-reviewer` for auth, RLS, server actions, or secrets; add `a11y-reviewer` for any UI change.
8. **Decide:** every reviewer `APPROVE` → queue for merge. `CHANGES_REQUESTED` → start a **fresh** worker with the consolidated scope: the original task file, every later instruction, the previous worker's report, the reviewer findings, and the branch (max 2 rounds; then `blocked`, log it, and ask the user). Resume an existing worker only when the work needs state that lives only there (an uncommitted checkout, a running dev server). A gate reported `SKIPPED` is not an approval.
   **You own every worker's output:** read the diff and evidence yourself and write your own summary; never pass a worker's "done" through unread.
9. **Merge** with `merge-train`, one branch at a time.
10. **Next wave:** recompute trust (step 5) and repeat from step 4.
11. **Report:** exit-condition state, a table of tasks (status, branch, evidence, screenshots), the trust level, and decisions needed.

## Autonomous runs ("run until done", overnight, `/loop`)
- Each wave must move the exit condition; log `progress` or `no_progress` per wave.
- **Stop after two consecutive `no_progress` waves.** You're stuck - surface it with the evidence; don't spin.
- **Never relax the exit condition, a gate, a budget, or a snapshot to declare victory.**
- Keep going on reversible work. Pause only for irreversible steps (push, deploy, any remote Supabase command, new dependency) - those wait for a human regardless of autonomy.
- Before context runs low or when asked to stop, use `pause-and-resume` (Pause).

## Settle forks by evidence, not by asking
Before asking the user "which approach?", check whether the answer is observable: which query plan is faster (`explain analyze` on local Supabase), which layout passes axe and fits the budget, which bundle is smaller. If it is, run a cheap probe in a throwaway worktree and let the result decide. Ask only for genuine preferences (brand, tone, product trade-offs) and irreversible actions.

## When the user corrects merged work
Log `human_rework` for the task (this lowers the trust level) and run `encode-lesson` so the mistake becomes a test, lint, policy test, or hook rule.

## Parallelism rules
- Parallel only when owned files are disjoint. Shared files (`package.json`, `src/styles/tokens.css`, `supabase/migrations/`, `src/lib/database.types.ts`) → one task owns them, others depend on it.
- Headless alternative: `scripts/agent-team/run-wave.sh T-011 T-012` (enforces the trust limit; `FORCE=1` overrides, log why).

## Never
- Merge without proof (`prove-it-works` evidence), a supervisor `APPROVE`, and green gates on the integration branch.
- Lower budgets or gate thresholds, update visual snapshots, or skip tests to get green.
- Push, deploy, touch a linked/remote Supabase project, or use the service-role key without explicit human approval.
