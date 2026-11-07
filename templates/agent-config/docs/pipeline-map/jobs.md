# Jobs, edge functions, webhooks

## What it is
Supabase Edge Functions (`supabase/functions/`), scheduled work (`pg_cron`), database webhooks, and inbound webhooks to route handlers.

## How to reach it
- `pnpm exec supabase functions serve <name>` then `curl -i` with a valid JWT, an invalid one, and none.
- Inbound webhooks: replay a recorded payload with its signature header against the local route handler.

## Evidence that counts
- Responses for authorized, unauthorized, and bad-signature calls; the structured log line for each run.
- For idempotent handlers: the same payload twice produces one effect.

## What usually lies
- A function tested with `--no-verify-jwt` locally but deployed with verification on (or the reverse).
- Webhook signature checks done on parsed JSON instead of the raw body.
