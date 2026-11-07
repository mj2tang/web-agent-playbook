# System design — <feature or app>

Status: draft | approved · Owner: · Date:

## Goals / non-goals / anti-goals
- Goal:
- Non-goal:
- Anti-goal (failure even if it works):

## Roles
| Role | Who | Stored where |
|---|---|---|
| anon | not signed in | — |
| authenticated | any signed-in user | `auth.users` |

## Data model
| Table | Purpose | Owner column | Key constraints | Indexes |
|---|---|---|---|---|

## Authorization (becomes pgTAP tests)
| Table | Role | select | insert | update | delete | Policy |
|---|---|---|---|---|---|---|

## API surface
| Operation | Runs as (server action / route handler / RPC / edge function) | Input schema | Output | Errors | Caller |
|---|---|---|---|---|---|

## Key flows
1.

## Failure modes
| Situation | Behaviour |
|---|---|
| Double submit | |
| Expired session | |
| Third-party timeout | |

## Observability
- Logs:
- Alerts:

## Security
- Secrets and where they live:
- Threats considered:

## Rollout and rollback
1.

## Open questions
- [ ] <question> — owner
