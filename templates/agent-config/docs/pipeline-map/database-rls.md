# Database and RLS

## What it is
Tables, constraints, RLS policies, and Postgres functions in `supabase/migrations/`, reached through the Supabase API with the anon key + user session.

## How to reach it
- `make db-check` (`supabase db reset`, `supabase test db`, RLS-on-every-table, type drift).
- Ad hoc as a role: `psql postgresql://postgres:postgres@127.0.0.1:54322/postgres` then `set role authenticated; set request.jwt.claims = '{"sub":"<uuid>","role":"authenticated"}';`.

## Evidence that counts
- pgTAP output listing allow **and** deny assertions for every changed policy.
- `supabase db reset` succeeding from zero (not just applying the new migration on an existing DB).
- `explain analyze` for new queries on seeded data, run as `authenticated`.

## What usually lies
- Queries run as `postgres` in Studio — superuser bypasses RLS.
- A denied select returns zero rows, not an error — a test asserting "no error" passes on a broken policy.
- Types generated before the last migration.
