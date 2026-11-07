---
name: supabase-migrations
description: Change the database only through new, reversible Supabase migrations run against the local stack - supabase migration new, write SQL with RLS in the same file as the table, prove it with supabase db reset and pgTAP, regenerate types - and never edit an applied migration or touch a linked/remote project. Use for any schema, policy, function, or seed change in a Supabase project. Not for pushing to production - that is a human step.
---

# Supabase migrations (local only)

## Procedure
1. `pnpm exec supabase start` (Docker) if it isn't running; `pnpm exec supabase status` shows the local URLs.
2. `pnpm exec supabase migration new <verb_object>` - e.g. `add_notes_archived_at`. One concern per migration.
3. Write the SQL:
   - New table → `alter table ... enable row level security;` and its policies **in the same migration** (`rls-policies`).
   - Additive first: add nullable column → backfill → set `not null` in a later migration, so the app can deploy between steps.
   - Write the down path as a comment block (`-- down: alter table ... drop column ...`) so a human can roll back.
4. Prove it from zero: `pnpm exec supabase db reset` (re-applies every migration + `seed.sql`).
5. Test: `pnpm exec supabase test db` (pgTAP in `supabase/tests/`).
6. Regenerate types: `pnpm exec supabase gen types typescript --local > src/lib/database.types.ts`.
7. `make db-check` runs 4-6 plus the RLS-on-every-table test and a type-drift check.

## Never (the guard hook blocks or asks)
- Edit a migration that is already committed - write a new one.
- `supabase link`, `supabase db push` (except `--local`), `--db-url` / `--project-ref` to a remote, `supabase functions deploy`, `supabase secrets set`.
- `supabase migration repair` or anything touching migration history without a human.
- Disable RLS on a public table.

## Done when
`make db-check` is green from a fresh `db reset`, and the regenerated types are committed with the migration.
