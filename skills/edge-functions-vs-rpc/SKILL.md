---
name: edge-functions-vs-rpc
description: Decide where backend logic runs in a Next.js + Supabase app - a Postgres function (RPC) for data-local logic under RLS, a server action for form mutations, a route handler for webhooks and public HTTP APIs, or a Supabase Edge Function for third-party secrets, scheduled work, or work outside the request - and record the choice in the design doc. Use when adding any backend operation or when a worker asks where logic should live. Not for pure UI logic.
---

# Where does this logic run?

| Need | Use | Why |
|---|---|---|
| Multi-row/transactional logic close to the data, must respect RLS | **Postgres function** (`security invoker`), called via `supabase.rpc()` | One round trip, atomic, RLS applies |
| Needs elevated rights for one narrow check (membership) | **`security definer` function** in a private schema, `set search_path = ''` | Narrow escalation, testable with pgTAP |
| Form submit / mutation from your own UI | **Server action** | Progressive enhancement, typed, same deploy as UI |
| Webhook receiver (Stripe, GitHub), public JSON API, file download | **Route handler** (`app/api/.../route.ts`) | Stable URL, raw body for signature checks |
| Uses a third-party secret you don't want in the Next.js app, or must run on a schedule / from a DB trigger | **Edge Function** (`supabase/functions/<name>`), cron via `pg_cron` + `pg_net` | Isolated secrets, runs without a request |
| React to row changes | **Database trigger** (small, synchronous) or **Edge Function via database webhook** (slow, external) | Keep triggers fast; push slow work out |
| Long-running jobs (> 30s) | A queue (`pgmq`) + worker Edge Function | Don't block requests |

## Rules
- Validate input with the Zod schema from `src/lib/contracts/` at every entry point, including RPC args (re-check in SQL with constraints).
- Edge Functions: verify the caller's JWT unless the function is a webhook with its own signature check; test locally with `pnpm exec supabase functions serve`. Deploying (`functions deploy`) is a human step.
- Record each operation's choice in the design doc's API surface table.

## Done when
Every operation in the design doc has a location and a reason, and its entry point validates input and checks the caller.
