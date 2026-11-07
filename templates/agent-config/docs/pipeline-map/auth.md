# Auth

## What it is
Sign-up, sign-in (password / magic link / OAuth), session refresh in `src/proxy.ts`, sign-out, and protected routes.

## How to reach it
- Playwright: sign up a new user against local Supabase, read the confirmation email from the local mail catcher (`supabase status` shows its URL), sign in, load a protected page, sign out.
- `curl -i localhost:3000/notes` without cookies → redirect to `/login`.

## Evidence that counts
- e2e run covering sign-in → protected page → sign-out, and the redirect for signed-out users.
- Server code paths use `auth.getUser()` (grep), not `getSession()`, for decisions.

## What usually lies
- A proxy redirect works but the page itself doesn't check the user (direct RSC requests still render).
- Expired-session behaviour untested — set a short JWT expiry in `supabase/config.toml` locally to check refresh.
