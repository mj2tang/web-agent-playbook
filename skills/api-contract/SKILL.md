---
name: api-contract
description: Freeze the contract that frontend and backend workers build against in parallel - the SQL schema and RLS policies in supabase/migrations, generated database types, and Zod input/output schemas in src/lib/contracts - and enforce that workers never change it without going back to the system-architect. Use after the system design doc is approved and before dispatching parallel frontend and backend tasks, or when a worker reports a contract mismatch. Not for internal helper types that never cross the client/server boundary.
---

# API contract

Parallel work only stays parallel if both sides agree on the shape first.

## What the contract is
1. **Schema + policies:** migrations in `supabase/migrations/` (tables, constraints, RLS policies, RPC signatures).
2. **Database types:** `src/lib/database.types.ts`, generated - never hand-edited: `pnpm exec supabase gen types typescript --local > src/lib/database.types.ts`.
3. **Boundary schemas:** `src/lib/contracts/<domain>.ts` - Zod schemas for every server action input, route handler body/response, and RPC argument, with exported inferred types.
4. **Behaviour:** the authorization table and error cases from `docs/design/system.md`, as pgTAP tests in `supabase/tests/`.

## Procedure (system-architect)
1. Write the migration(s) and pgTAP tests from the design doc; `make db-check` green.
2. Regenerate types; write the Zod schemas; Vitest for each schema's valid/invalid examples.
3. Commit as `contract: <domain>` and merge before wave 1. Record the contract commit SHA in `tasks/EPIC.md`.

## Rules for workers
- Import types from `database.types.ts` and schemas from `src/lib/contracts/`; don't redeclare shapes.
- Need a new column, policy, or field? Return `STATUS: blocked` with the proposed change. The architect updates the contract in its own task.
- `db-check` fails if generated types drift from the migrations.

## Done when
Contract merged, types regenerated, schemas tested, and the contract SHA is recorded in the epic.
