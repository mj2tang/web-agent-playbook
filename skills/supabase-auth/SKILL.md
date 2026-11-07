---
name: supabase-auth
description: Wire Supabase Auth into Next.js correctly - @supabase/ssr createServerClient in server code and createBrowserClient in client components, session refresh in middleware, auth.getUser() (never getSession()) for authorization decisions, protected routes on the server, and the service-role key only in server-only modules. Use when adding sign-in, sign-up, OAuth, protected pages, or any code that reads the current user. Not for authorization rules inside the database - see rls-policies.
---

# Supabase Auth in Next.js

## Clients (`src/lib/supabase/`)
- `server.ts`: `createServerClient(url, anonKey, { cookies })` using `cookies()` from `next/headers`. Use in server components, server actions, route handlers.
- `client.ts`: `createBrowserClient(url, anonKey)`. Use only in `"use client"` components.
- `middleware.ts` + `src/middleware.ts`: refresh the session on every request (`supabase.auth.getUser()` inside middleware) and copy cookies to the response. Without this, server code sees expired sessions and RLS treats users as `anon`.

## Rules
- **Authorization uses `supabase.auth.getUser()`** - it validates the JWT with the auth server. `getSession()` reads the cookie unverified; fine for UI hints, never for decisions.
- **Protect on the server:** in the page or layout, `const { data: { user } } = await supabase.auth.getUser(); if (!user) redirect('/login')`. Middleware redirects are a convenience, not the guard.
- **Every server action re-checks the user** - actions are POST endpoints anyone can call.
- **Service role** (`SUPABASE_SERVICE_ROLE_KEY`) bypasses RLS. Only in `src/lib/server/` modules that `import "server-only"`, never in `NEXT_PUBLIC_*`, never in client components (the guard hook blocks it). Prefer RLS + the user's session over the service role.
- OAuth/magic link: a route handler at `/auth/callback` exchanges the code (`exchangeCodeForSession`) and redirects to a same-origin path only (no open redirects).
- Sign-out: server action calling `supabase.auth.signOut()` then `redirect('/')`.
- Local email: Supabase local stack captures emails in Inbucket/Mailpit (`supabase status` shows the URL) - use it in e2e tests.

## Done when
Signed-out users are redirected on the server for every protected route, server actions reject unauthenticated calls (test it with `curl` without cookies), and no client bundle references the service-role key.
