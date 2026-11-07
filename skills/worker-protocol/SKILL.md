---
name: worker-protocol
description: The contract every worker agent follows - claim one task file, stay inside its owned files in an isolated worktree, build against the frozen contract and design tokens, work test-first, run the gates, commit, and return a fixed summary. Use whenever you are executing a task from tasks/ as a worker. Not for the orchestrator, architect, designer, or reviewer roles.
---

# Worker protocol

## Shell discipline
- **One command per Bash call.** No `&&`, `;`, pipes, `cd dir && ...`, or `sed -i`: compound commands need separate approval for every part and stall headless runs. Use the Edit tool to change files and run commands from the project root (git worktrees: `git -C <path> ...`).

## Steps
1. **Read** the task file, `AGENTS.md`, the contract (`docs/design/system.md`, `src/lib/contracts/`, the migrations) and, for UI, `src/styles/tokens.css` and the component spec. If the task is ambiguous or conflicts with the code or the contract, stop and return `STATUS: blocked` with the question - don't guess.
2. **Branch:** you are in your own worktree. Create/checkout `task/<id>-<slug>` if you're not already on it.
3. **Stay in scope:** edit only the task's owned files (plus new test files). Need another file, or a contract change? Return `blocked` and say why - contract changes go back to the `system-architect`.
4. **Test first** (`tdd-loop`): write failing tests from the acceptance criteria (Vitest unit, pgTAP for SQL/RLS, Playwright for pages), then implement.
5. **Gates:** run `make check`, plus `make db-check` when the task touches `supabase/`, and `make ui-check` when it touches pages or components (in repos without a Makefile: `scripts/gates/check.sh`, `db-check.sh`, `ui-check.sh`). Fix until green. Never weaken a test, budget, threshold, or snapshot. A gate that prints `SKIPPED` is reported as skipped, never as pass.
5a. **Commit, then prove.** Commit your change before running the proof commands so evidence records a clean SHA.
    **Codex (run-wave):** the `workspace-write` sandbox keeps `.git` read-only, so you can't commit. Don't retry or report it as a blocker: run the gates on your final changes, leave them uncommitted, and the runner commits your owned files when you exit. The supervisor runs the proof on that commit.
5b. **Prove it** (`prove-it-works`): exercise every `docs/pipeline-map/` entry point the change can affect on this branch's HEAD, and log one `verify` row per entry point with its evidence pointer (screenshot, Playwright report, pgTAP output, `curl` transcript).
5c. **Settle forks by evidence:** if you're unsure between two approaches and the answer is observable (a query plan, a bundle size, an axe result), run a quick probe instead of returning `blocked`. Block only for genuine scope or preference questions.
6. **Commit** small logical commits: `T-<id>: <what>`. Do not push or merge.
7. **Update** the task file's `status: review` and fill the "Worker notes" section.
8. **Return exactly:**
```
STATUS: done | blocked
TASK: T-<id>  BRANCH: task/T-<id>-<slug>
CHANGED: <files>
GATES: check=pass db-check=<pass|n.a.|skipped> ui-check=<pass|n.a.|skipped>
EVIDENCE: <pipeline-map entry points covered → artifact each; unreachable ones and why>
NOTES: <risks, follow-ups, questions - 3 lines max>
```
