---
name: security-review
description: Review a web change for security against the OWASP Top 10 as it shows up in Next.js + Supabase - broken access control (missing RLS or server-action auth checks), injection, secrets in client bundles or NEXT_PUBLIC_ vars, the service-role key, open redirects, SSRF, XSS through dangerouslySetInnerHTML, CSRF, insecure headers, and vulnerable dependencies - with a concrete exploit per finding. Use for any change touching auth, RLS, server actions, route handlers, edge functions, file uploads, or secrets, and before any release. Not for pure styling changes.
---

# Security review

Only report findings you can tie to a file:line and a concrete attack ("as user B, POST this to the action and read A's note").

## Checklist
1. **Access control (A01):** every new table has RLS + policies + pgTAP deny tests; every server action and route handler calls `auth.getUser()` and checks ownership/role before acting; IDs from the client are never trusted for ownership.
2. **Secrets (A02/A05):** no secrets in `NEXT_PUBLIC_*`, client components, logs, or the repo (`.env*` ignored, `.env.example` has placeholders only). Service-role key only in `server-only` modules.
3. **Injection (A03):** no SQL string concatenation in RPC/functions (`format()` with `%L`/`%I`, or parameters); no `dangerouslySetInnerHTML` with user content (sanitise with a vetted library if unavoidable); no `eval`/`new Function`.
4. **Insecure design (A04):** rate limits on sign-in, sign-up, password reset, and expensive actions; idempotency on payments and webhooks.
5. **Misconfiguration (A05):** security headers in `next.config.ts` (CSP, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors`); storage buckets private unless intended; CORS on route handlers is explicit.
6. **Vulnerable components (A06):** `pnpm audit --prod` - high/critical need a fix or a written exception.
7. **Auth failures (A07):** `getUser()` not `getSession()` for decisions; redirects after login restricted to same-origin paths.
8. **Integrity (A08):** webhook signatures verified on the raw body; no unpinned remote scripts.
9. **Logging (A09):** auth failures and permission denials logged without tokens or PII.
10. **SSRF (A10):** any "fetch this URL" feature validates scheme and host against an allow list and blocks private ranges.

## Output
```
VERDICT: APPROVE | CHANGES_REQUESTED
FINDINGS:
1. [critical|high|medium|low] file:line — OWASP A0x — attack scenario — fix
```
