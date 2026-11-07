# Task board

Status: `todo` → `in_progress` → `review` → `done` (or `blocked`). The orchestrator keeps this table in sync with the task files.

| ID | Title | Type | Owner | Status | Depends on | Branch |
|---|---|---|---|---|---|---|
| T-001 | Example: archive notes (contract) | contract | system-architect | todo | — | task/T-001-archive-contract |
| T-002 | Example: archive action + RPC | backend | backend-worker | todo | T-001 | task/T-002-archive-backend |
| T-003 | Example: archive button + archived view | frontend | frontend-worker | todo | T-001 | task/T-003-archive-ui |
