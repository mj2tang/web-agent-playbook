---
name: rls-policies
description: Write Supabase row-level security that is on for every public table, explicit per role (anon, authenticated) and per operation (select, insert, update, delete), uses (select auth.uid()) for performance, checks ownership on both using and with check, and is proven by a pgTAP test for each allow and each deny. Use whenever a migration adds or changes a table, a policy, a role, or a security definer function. Not for application-level authorization in server actions - do both.
---

# RLS policies

RLS is the real authorization layer: the anon key is public, so anything RLS allows, anyone can do.

## Rules
- `alter table public.<t> enable row level security;` for **every** table in `public`, in the migration that creates it. `make db-check` fails otherwise (`supabase/tests/rls_enabled.test.sql`).
- **One policy per operation and role**, named for what it allows: `"owners can update their notes"`.
- Target roles explicitly: `to authenticated` (or `to anon` for genuinely public reads). Never rely on the default `public` role.
- Ownership: `using ((select auth.uid()) = owner)` and, for insert/update, `with check ((select auth.uid()) = owner)` - otherwise users can move rows to someone else.
- Wrap `auth.uid()` / `auth.jwt()` in `(select ...)` so Postgres evaluates it once per query; index the owner column.
- Membership checks go through a `security definer` function in a non-exposed schema with `set search_path = ''`, returning a boolean; grant execute only to `authenticated`.
- Never use `user_metadata` in policies (users can edit it). `app_metadata` only if set server-side.
- Views: `with (security_invoker = true)` so they respect RLS.
- Storage buckets need their own policies on `storage.objects`.

## Test every policy (pgTAP)
```sql
begin;
select plan(3);
-- as user A
set local role authenticated;
set local request.jwt.claims = '{"sub":"<uuid-a>","role":"authenticated"}';
select is((select count(*) from public.notes where owner = '<uuid-b>')::int, 0, 'A cannot see B''s notes');
select throws_ok($$update public.notes set owner = '<uuid-b>' where owner = '<uuid-a>'$$, null, 'A cannot reassign a note');
reset role;
set local role anon;
select is((select count(*) from public.notes)::int, 0, 'anon sees nothing');
select * from finish();
rollback;
```
Note: RLS denials on select return **zero rows**, not errors - assert counts.

## Done when
Every table × role × operation in the design doc's authorization table has a policy (or is denied by default) and a passing pgTAP assertion for allow and deny.
