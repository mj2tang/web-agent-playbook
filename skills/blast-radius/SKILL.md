---
name: blast-radius
description: Before a change ships, find what it could break outside the diff in a web app - routes that render a shared component, everything a token or Tailwind theme change restyles, queries and policies a migration affects, server actions and clients that share a schema - and prove the one fact it's safe because of by running code, not by writing it up. Use for "what could this break", "blast radius of X", a small diff you don't trust, or before merging a change to shared UI, tokens, the contract, or auth. Not for listing callers only - grep does that.
---

# Blast radius

After Lauren Tan's pstack `blast-radius`, for web apps. Listing callers isn't the job; finding the breakage grep won't show you is.

## How sure are you (get each key fact as far down as is cheap, and say where it stopped)
1. You said so. Worthless alone.
2. You pointed at it: a real `file:line`, or the library's own source.
3. You walked the failure step by step and showed it can't happen.
4. **You ran it**: a test or script that calls the real code and fails loudly if you're wrong.
5. **You reproduced it in the running app**: the page in a browser, the action with `curl`, the query as `authenticated`.

## Where web changes break things grep misses
| Change | Look at |
|---|---|
| Shared component or its props | Every route that renders it (`docs/pipeline-map/routes.md`), every state, both themes, 3 widths |
| Token, `globals.css`, Tailwind `@theme` | Everything: run the full screenshot suite against committed baselines |
| Migration, policy, function | Every query on that table, generated types, RLS as `anon` / `authenticated` / another user, existing rows (backfill), the seed |
| Zod schema / contract | Both sides: forms (client), server actions and route handlers (server), database constraints |
| Auth, session, `src/proxy.ts` | Protected pages, server actions without a session, cookie refresh, redirects |
| Server ↔ client boundary (`"use client"`, server-only imports) | Bundle size, secrets reaching the client, hydration |
| Dependency upgrade | Its changelog and source at the pinned version, not your memory of it |

## Steps
1. Read the change, including what it now does differently that the diff doesn't spell out.
2. Find the **one fact** it's safe because of ("this token is only used by `Button`", "this policy only narrows select"). If it holds, most risks clear at once.
3. Look where grep stops: the table above, the library's source, when things run (server vs client, render vs effect), JSON and column shapes, feature flags.
4. Rate each risk honestly (likelihood, cost). Keep confirmed risks; list checked-and-cleared ones separately. Cite real `file:line`; never invent a caller.
5. **Prove the one fact** at step 4 or 5 and paste the output.
6. For a wide change, ask a second model the same question (skill `interrogate`); different models catch different bugs.

## Hand back
- **What it does**, including the non-obvious part.
- **The one fact it's safe because of**, the step you reached, and the proof (or "unproven").
- **Risks**: how it breaks, `file:line`, likelihood and cost, how to check.
- **Cleared**: what you checked and why it's fine.
- **Before you merge**: the cheapest test or repro that would catch the real bug (include your script).
