# Backend architecture

The starter's backend is Supabase (Postgres, Auth, Storage, Edge Functions) behind a Next.js App Router frontend. The skills also work for other Postgres backends, minus the Supabase specifics.

## Design before code
`system-design-doc` produces `docs/design/system.md`: goals, roles, data model, an **authorization table** (table × role × operation → policy), the API surface, key flows, failure modes, observability, security, and rollout. The authorization table becomes pgTAP tests.

## Where logic runs
| Need | Use |
|---|---|
| Data-local, transactional, under RLS | Postgres function via `supabase.rpc()` |
| Form mutations from your UI | Server action (validate with Zod, check `auth.getUser()`) |
| Webhooks, public JSON API | Route handler (verify signatures on the raw body) |
| Third-party secrets, schedules, background work | Edge Function (+ `pg_cron` / queues) |
Details in `edge-functions-vs-rpc`.

## Authorization in two layers
1. **RLS** on every public table, explicit per role and operation, `(select auth.uid())`, `with check` on writes, pgTAP allow and deny tests. The publishable key is public; RLS is the real boundary.
2. **Server code** re-checks the user in every server action and route handler, and validates input with the contract's Zod schema.

## Observability
Structured JSON logs with request IDs, `error.tsx` per segment, `instrumentation.ts` for error reporting, `/api/health` checking the database (`observability`).
