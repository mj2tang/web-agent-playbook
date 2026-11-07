# Supabase

## Local only, by design
Agents work against the local stack (`pnpm exec supabase start`, Docker). The guard hook blocks `supabase link`, `db push` without `--local`, `functions deploy`, `secrets set`, `--db-url`, `--project-ref`, and `psql` to non-local hosts. Promoting migrations to a hosted project is a human step.

## Commands agents use
| Command | Purpose |
|---|---|
| `pnpm exec supabase start` / `status` / `stop` | local stack (status shows URLs, keys, and `MCP_URL`) |
| `pnpm exec supabase migration new <name>` | new migration (never edit an applied one) |
| `pnpm exec supabase db reset` | re-apply all migrations + seed from zero |
| `pnpm exec supabase test db` | pgTAP tests in `supabase/tests/` |
| `pnpm run db:types` | regenerate `src/lib/database.types.ts` |
| `make db-check` | all of the above as one gate, plus "every public table has RLS" and type drift |

## The RLS gate
`supabase/tests/rls_enabled.test.sql` fails if any table in `public` lacks row level security and names the tables. Verified on the starter: adding `create table public.leaky (id int)` fails `db-check` with `have: leaky`. A weakened policy (`using (true)`) fails the notes policy tests.

## Running next to another local Supabase project
Each project's stack binds the default ports (54321-54327). Stop the other project (`supabase stop` there) or change the ports in `supabase/config.toml`; `make env` reads whatever the running stack reports.

## CLI notes (Nov 2026, supabase CLI 3.0)
- `gen types --local` prints a deprecation note: local is the default and the flag goes away in v4.
- `supabase status -o env` includes `PUBLISHABLE_KEY` (preferred) and `ANON_KEY`.
- The local stack serves an MCP endpoint at `<API_URL>/mcp`.
