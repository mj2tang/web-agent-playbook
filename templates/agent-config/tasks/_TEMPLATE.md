---
id: T-000
title: <short imperative title>
type: contract | design | backend | frontend | integration
worker: system-architect | ui-designer | backend-worker | frontend-worker
status: todo
depends_on: []
branch: task/T-000-<slug>
owned_files:
  - src/...
  - tests/...
---

## Objective
<What a user can do, or what is true, when this is done - one or two sentences.>

## Contract and design
- <links: docs/design/..., src/lib/contracts/..., supabase/migrations/..., docs/design/components/...>

## Acceptance criteria (each checkable by a command)
- [ ] `pnpm exec vitest run tests/unit/...` passes, including new tests for: <cases>
- [ ] `make check` passes
- [ ] `make db-check` passes, with pgTAP allow/deny tests for: <policies> (if supabase/ changes)
- [ ] `make ui-check` passes: axe clean on <routes>; screenshots for <states> at 375/768/1280 (if UI changes)

## Out of scope
- <things the worker must not change - always: the contract, tokens, gates>

## Decision log
- <date> — <decision> — <why>

## Worker notes
<Filled by the worker: what changed, gate output summary, evidence, risks.>

## Supervisor verdict
<APPROVE | CHANGES_REQUESTED + findings>
