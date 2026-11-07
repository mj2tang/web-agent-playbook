---
name: data-modeling
description: Design Postgres schemas for Supabase - one owner/tenant column per table, real constraints (not null, check, unique, foreign keys with on delete behaviour), uuid or identity keys, timestamptz, indexes for every RLS predicate and foreign key, and normalisation with deliberate exceptions - and check query plans with explain analyze on local data. Use when adding or changing tables, columns, relationships, or slow queries. Not for client-side state or caching.
---

# Data modeling (Postgres on Supabase)

## Rules
- **Keys:** `id uuid primary key default gen_random_uuid()` (or `bigint generated always as identity` for internal tables).
- **Ownership:** every user-data table has an owner or tenant column (`owner uuid not null references auth.users on delete cascade default auth.uid()`, or `org_id` + a `memberships` table). RLS depends on it.
- **Constraints in the database,** mirrored in Zod: `not null` by default, `check (length(body) between 1 and 2000)`, `unique` for natural keys, enums via `check (status in (...))` or a lookup table.
- **Time:** `timestamptz not null default now()`; `updated_at` maintained by a trigger, not by clients.
- **Indexes:** on every foreign key and every column an RLS policy filters on (`owner`, `org_id`). Composite indexes match query order.
- **Deletes:** decide `cascade`, `restrict`, or soft delete (`deleted_at` + policy filter) per relationship and write it in the design doc.
- **No secrets or derived data** in user-writable columns; computed values via views or generated columns.
- **Schema:** app tables in `public` (exposed through the API, so RLS on all of them); private helpers in a non-exposed schema (`private`).

## Check
- `explain analyze` the main queries against seeded local data (`supabase/seed.sql` with realistic row counts) as the `authenticated` role - RLS adds predicates the plan must handle.
- Supabase's linter: `pnpm exec supabase db lint` (local).

## Done when
Migrations apply from zero (`supabase db reset`), every table has an owner column with an index, and constraints match the Zod schemas.
