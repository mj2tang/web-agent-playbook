# Claude Code

🟠 Tips specific to [Claude Code](https://code.claude.com/docs). Dated November 2026.

## Memory files
- `CLAUDE.md` at repo root (shared), `CLAUDE.local.md` (personal, gitignored), `~/.claude/CLAUDE.md` (all projects). Nested `CLAUDE.md` files load when working in that directory.
- Share one source of truth with Codex: `CLAUDE.md` containing `@AGENTS.md` plus Claude-only notes (what this playbook scaffolds).
- `/init` drafts a starting file — then trim it.

## Subagents (`.claude/agents/*.md`)
- Frontmatter: `name`, `description` (required), plus `tools`, `model`, `skills` (preloaded into context), `isolation: worktree` (own temporary git worktree), `background`, `permissionMode`, `memory`, `hooks`.
- `claude --agent orchestrator` (or `"agent": "orchestrator"` in `.claude/settings.json`) makes the **main session** take on an agent's prompt, tools, and model — that's how the orchestrator runs here.
- Subagents can spawn subagents (default depth 3; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`). Remove `Agent` from `tools` to stop a role from delegating.
- Give reviewers read-only tools; give workers `isolation: worktree` for safe parallelism.

## Skills (`.claude/skills/<name>/SKILL.md`)
- Same Agent Skills format Codex uses — this playbook keeps one copy in `.agents/skills/` and symlinks `.claude/skills` to it.
- Loaded on demand by description; preload into a subagent with `skills:`.

## Hooks
- Deterministic automation in `settings.json` → `hooks`: `PreToolUse` (exit 2 blocks with a message to Claude), `PostToolUse`, `Stop`, `SessionStart`, `PreCompact`, …
- This playbook's `guard.py` blocks push/reset/deploys and any linked or remote Supabase command (`link`, `db push` without `--local`, `functions deploy`, `--db-url`, non-local `postgres://`), blocks the service-role key in client code, protects `.env*`, `configs/gates.json`, and visual snapshots, asks before new dependencies, snapshot updates, and edits to committed migrations, and runs prettier on edited files. It splits commands on `;`, `&&`, `||`, and `|` and tokenises each one (so `npx supabase@latest db push`, `supabase --workdir . db push`, and `db push --linked; echo --local` are caught), and asks about Supabase subcommands it doesn't know. It is still a best-effort text matcher, not a sandbox: a package script or a shell function can hide a command, so keep the human-approval list in `AGENTS.md` and review what agents run.
- Rule of thumb: must *always* happen → hook; needs judgement → skill.

## Permissions
- `permissions.allow` for the gate commands and local Supabase, `ask` for push and new deps, `deny` for secrets and gate budgets. `Edit(...)` rules cover all file-editing tools.

## Plugins
- A plugin bundles skills, agents, hooks, MCP servers: `.claude-plugin/plugin.json` + default folders. Validate with `claude plugin validate .`.
- Team auto-install: `extraKnownMarketplaces` + `enabledPlugins` in the project's `.claude/settings.json` (what `playbook.py init --mode plugin` writes).

## Seeing the UI
- Add the Playwright MCP server (`claude mcp add playwright -- npx -y @playwright/mcp@latest`) so agents can navigate, resize, and screenshot pages during `visual-review`.

## Session habits
- Plan mode (Shift+Tab) for non-trivial work; `/clear` between tasks; `/compact` on long sessions.
- `claude -p "…"` for headless runs (scripts, CI, `run-wave.sh`).
- When you correct an agent twice, run the `encode-lesson` skill: turn the lesson into a test, pgTAP test, lint, or hook rule, and use `AGENTS.md` text only for judgment calls.
