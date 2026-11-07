---
name: system-design-doc
description: Write the system design doc for a feature or new app before code - goals and non-goals, users and roles, data model, RLS and authorization model, API surface (server actions, route handlers, RPC, edge functions), sequence of key flows, failure modes, observability, security, and rollout - in docs/design/system.md using the template. Use for any new app, any feature that adds tables, roles, external integrations, or background work, and whenever the system-architect is asked to freeze a contract. Not for UI-only changes or small fixes inside an existing design.
---

# System design doc

The design doc is the argument; the contract (`api-contract`) is what it freezes.

## Procedure
1. **Copy** `assets/system-design-template.md` to `docs/design/system.md` (or `docs/design/<feature>.md`).
2. **Goals / non-goals / anti-goals** - one line each, user-visible.
3. **Roles:** who is `anon`, who is `authenticated`, any app roles (owner, member, admin) and how they are stored (a `memberships` table, not JWT custom claims, unless there's a reason).
4. **Data model** (`data-modeling`): tables, keys, constraints, indexes, ownership column per table.
5. **Authorization:** for every table × role × operation, allowed or denied, and the policy that enforces it (`rls-policies`). This table becomes pgTAP tests.
6. **API surface:** for each operation, where it runs (`edge-functions-vs-rpc`), its input schema (Zod), output, errors, and who may call it.
7. **Key flows:** a numbered sequence (or Mermaid sequence diagram) for each of the 2-3 flows that matter: sign-in, the core write, any webhook/background job.
8. **Failure modes:** what happens on duplicate submit, concurrent edit, partial failure of a multi-step write, third-party timeout, expired session.
9. **Observability and security:** what is logged, what alerts, which secrets exist and where they live (`observability`, `security-review`).
10. **Rollout:** migration order, backfill, feature flag, how to roll back.
11. **Open questions** - each with an owner.

## Done when
Every section is filled or explicitly "n/a - why", the authorization table covers every table × role × operation, and the owner has approved the doc.
