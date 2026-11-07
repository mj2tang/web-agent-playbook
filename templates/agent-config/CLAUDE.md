@AGENTS.md

## Claude Code
- Team mode: `claude --agent orchestrator`. `system-architect` and `ui-designer` go first; `frontend-worker` / `backend-worker` run in isolated worktrees; `supervisor` gates merges.
- Solo mode: plan mode for anything non-trivial, then `verify-before-done` before finishing.
- Screenshots: the Playwright MCP server (`/mcp`) for interactive visual checks.
- Guard hooks block pushes, deploys, remote Supabase, secrets, snapshots, and gate files, and ask before new dependencies; ask the user instead of working around them.
