# Server actions and API routes

## What it is
Server actions (`"use server"`) and route handlers under `src/app/**/route.ts` — public HTTP endpoints, whatever the UI does.

## How to reach it
- Through the UI with Playwright (happy path and validation errors).
- Directly: `curl -i -X POST localhost:3000/api/...` with and without a session cookie; for server actions, submit the form with JS disabled.

## Evidence that counts
- Status codes and bodies for: valid input, invalid input (Zod errors), signed out (401/redirect), another user's resource (403/404, never 200).
- Vitest output for the input schema.

## What usually lies
- Testing only through the UI, which hides the missing auth check (the action is still callable directly).
- A test client created with the service-role key — it bypasses RLS, so "works" proves nothing about authorization.
