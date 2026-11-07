---
name: observability
description: Make a web app debuggable in production - structured server logs with request IDs, error boundaries and error.tsx per route segment, error reporting, a health route that checks the database, and Postgres/Supabase logs - without logging secrets or personal data. Use when adding server actions, route handlers, edge functions, or background jobs, or when a failure couldn't be diagnosed from logs. Not for local debugging sessions - see systematic-debugging.
---

# Observability

## Minimum for every app
- **Errors:** `app/error.tsx` and `app/global-error.tsx`, plus `error.tsx` in segments with their own data. Show recovery copy (`ux-copy`), log the error server-side with a digest.
- **Instrumentation:** `instrumentation.ts` with `onRequestError` forwarding to the error reporter the project uses (Sentry, etc.); none configured → structured `console.error` JSON.
- **Structured logs** in server actions, route handlers, and edge functions: one JSON line per event with `event`, `request_id`, `user_id` (not email), `duration_ms`, `outcome`. Never tokens, cookies, passwords, or full request bodies.
- **Health:** `app/api/health/route.ts` returns 200 with `{ db: "ok" }` after a cheap query (`select 1` via RPC), 503 otherwise. No auth details in the response.
- **Database:** slow-query visibility via `pg_stat_statements` (enabled on Supabase); review in Supabase Studio locally.
- **Background jobs:** every job logs start/finish/failure with an ID and retries with backoff; failures land somewhere a human looks.

## Done when
A failing server action produces one structured log line with a request ID and the user sees recovery copy, and `/api/health` reflects database availability.
