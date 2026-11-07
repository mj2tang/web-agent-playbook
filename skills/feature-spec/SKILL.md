---
name: feature-spec
description: Write a task file on the agent task board (tasks/T-NNN-slug.md) with objective, owned files, acceptance criteria that a command can check (tests, gates, screenshots, budgets), and dependencies, so a worker agent can execute it without further questions. Use when decomposing work for parallel agents or before starting any non-trivial web feature. Not for one-line fixes or pure questions.
---

# Feature spec (task file)

Copy `tasks/_TEMPLATE.md` to `tasks/T-NNN-<slug>.md` and fill every field:

- **Objective:** one sentence, user-visible ("A signed-in user can archive a note from /notes").
- **owned_files:** the exact files the worker may edit (front matter list). Two tasks in a wave never share one.
- **Contract:** the tables, policies, Zod schemas, and component spec this task builds against (links). Workers don't change them.
- **Acceptance criteria**, each checkable by a command:
  - `pnpm test tests/unit/archive.test.ts` passes with new cases for empty, too long, not owner
  - `make db-check` passes with a pgTAP test proving user B can't archive user A's note
  - `make ui-check` passes: axe has no serious/critical issues on `/notes`, and screenshots at 375/768/1280 match `docs/design/components/note-card.md`
  - `/notes` JS stays within the route budget in `configs/gates.json`
- **Depends on:** task IDs that must be `done` first.

## Decomposition order for web work
1. Contract (system-architect): schema + RLS + Zod + system design doc, with pgTAP tests. Design (ui-designer): brief, tokens, component specs.
2. Backend tasks (backend-worker): migrations, RPC, server actions, edge functions - against the contract.
3. Frontend tasks (frontend-worker): pages and components - against the same contract and tokens; parallel with step 2.
4. Integration: one end-to-end Playwright journey across the feature (orchestrator or a worker that owns `tests/e2e/`).
