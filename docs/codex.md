# OpenAI Codex

🔵 Practices for [Codex](https://openai.com/codex/), drawn from the [OpenAI developers blog](https://developers.openai.com/blog/) and Codex docs, plus daily use. Dated November 2026 — check the docs for changes.

## AGENTS.md
- Codex builds an instruction chain once per run: `~/.codex/AGENTS.md` (or `AGENTS.override.md`), then one file per directory from the repo root down to the working directory. Closer files come later and win. Combined size is capped (`project_doc_max_bytes`, 32 KiB default).
- **Prune regularly.** Remove instructions that newer models follow anyway (e.g. "always run tests") — they cause over-testing and bloat.
- **Tie docs to situations**: "when changing a schema, read `docs/schema.md`" beats "read all docs before every edit".
- **Explicitly allow known-safe workflows** (local test suite, disposable data) so the agent doesn't stop to ask at every step; reserve "ask first" for genuinely irreversible actions.
- **Code review rules** go in a `## Code Review Rules` section (root or nested `AGENTS.md`). Good rules protect a consequential, non-obvious invariant, state the risk and a safe alternative, and describe outcomes rather than file names. Leave formatting to linters. Test a new rule on a PR with one violating change, one safe counterexample, and one unrelated change. Trigger with `@codex review`.

## Skills
- Codex discovers skills in `.agents/skills/` (from the working directory up to the repo root), `~/.agents/skills/`, and `/etc/codex/skills`. Invoke explicitly with `$skill-name` or `/skills`; otherwise Codex picks by description.
- **Descriptions are routing rules:** say when to use, when *not* to, and what success looks like. Add near-miss negatives — teams have seen ~20% routing gains from this.
- Keep `SKILL.md` a lean router; put templates, examples, and scripts in `references/`, `assets/`, `scripts/` so they load only when needed.
- Prefer goals and guidance over rigid step lists for strong models; keep fixed contracts (output formats, gate commands) explicit.
- For production workflows with a fixed contract, **name the skill in the prompt** rather than relying on implicit routing.
- Optional `agents/openai.yaml`: UI metadata, `policy.allow_implicit_invocation: false` for explicit-only skills, and `dependencies.tools`.

## Long-horizon tasks
- **Freeze the target** in a spec file: goals, non-goals, constraints, "done when" checks. (`tasks/EPIC.md` in this playbook, with the frozen contract SHA.)
- **Milestones in a plan file**, each small enough for one loop, with validation commands.
- **Stop-and-fix:** if validation fails, repair before the next milestone.
- **Decision log + status log** in files so the agent doesn't reverse earlier choices and you can audit after stepping away.
- Use `/plan` to align before edits; steer mid-run instead of restarting.
- **Parallelise across threads, isolate with git worktrees** (`codex exec --worktree` or your own worktrees).

## Headless and CI
- `codex exec "<prompt>"` runs non-interactively. `--json` emits an event trace you can assert on; `-C <dir>` sets the working root; `--output-schema` enforces structured output; `--add-dir` makes extra paths writable.
- **Pass the sandbox explicitly.** Verified on codex-cli 0.167 (Nov 2026): `-p/--profile <name>` layers `$CODEX_HOME/<name>.config.toml` from your *user* config, not a profile table in the project, and a project's `.codex/config.toml` `sandbox_mode` was not applied over a user config that sets `danger-full-access`. So this playbook's scripts always pass `--sandbox workspace-write -c sandbox_workspace_write.network_access=<true|false>`; the project `.codex/config.toml` only carries defaults and MCP servers.
- **`.git` is read-only** in `workspace-write` (worktrees too, even with `--add-dir`), so headless Codex workers can't commit. `run-wave.sh` commits each worker's `owned_files` after it exits and reports anything outside them. `CODEX_APPROVE_FOR_ME=1` adds `--approve-for-me`, which routes blocked commands through Codex's automatic reviewer (it approves any blocked command, not just commits); the sandbox flags stay.
- **No network for workers.** `run-wave.sh` installs the worktree's dependencies (`pnpm install --frozen-lockfile`) *before* dispatch and adds the pnpm store with `--add-dir`.
- **Gates that need Docker, localhost, or browsers** (`db-check`, `ui-check`) run in the supervisor's review with network on:
  ```bash
  codex exec --sandbox workspace-write -c sandbox_workspace_write.network_access=true --add-dir <worktree> \
    "Act as the supervisor defined in .claude/agents/supervisor.md. Review branch task/T-001-<slug> against tasks/T-001-<slug>.md."
  ```

## Custom agents
- Codex custom agents are TOML files in `.codex/agents/` (project) or `~/.codex/agents/`: `name`, `description`, `developer_instructions`, optional `model`, `model_reasoning_effort`, and feature switches. Sandbox, approvals, and MCP servers always come from the parent session.
- This playbook generates one per role from `agents/*.md` (`playbook.py init`/`new`; `sync` updates them and keeps your edits). Verified on codex-cli 0.167: Codex lists all nine next to its built-ins (`default`, `explorer`, `worker`).
- Codex spawns a custom agent only when the prompt, `AGENTS.md`, or a skill asks for it by name. Cap parallel threads with `[agents] max_concurrent_threads_per_session` in `.codex/config.toml`.

## Hooks
- Hooks are stable and on by default (`codex features list` shows `hooks stable true` on 0.167). They go in `[hooks]` in `config.toml` (user or project layer) or `hooks.json`; events include `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `SubagentStart`/`SubagentStop`.
- Payloads follow Claude Code's shape: shell commands arrive as `tool_name: "Bash"`, `tool_input: {"command": ...}`; file edits as `tool_name: "apply_patch"`, `tool_input: {"command": "<the whole patch>"}`. Exit 2 with stderr blocks; `hookSpecificOutput.permissionDecision: "ask"` asks. So this playbook registers the same `guard.py` for Codex (`matcher = "Bash"` and `matcher = "apply_patch"`), which parses patches file by file.
- **Trust:** Codex hashes each hook and runs it only after you trust it (startup review or `/hooks`). Verified: a headless `codex exec` in a fresh project skipped the untrusted project hooks without a warning and ran `git push`. Trust them once interactively before running `run-wave.sh` with `RUNNER=codex`. `--dangerously-bypass-hook-trust` exists for vetted automation; don't use it on repos you haven't read.
- Hook commands run from the session's working directory, so start Codex at the install root.

## Approvals and sandbox
- Least privilege that keeps you flowing: read-only to explore, workspace-write to implement, full access only inside an externally sandboxed environment.
- Keep network off unless a task needs it; allowlist the minimum domains.

## MCP servers
- `.codex/config.toml` (rendered by this playbook) adds the **local** Supabase MCP endpoint (`url = "http://127.0.0.1:54321/mcp"`, served by `supabase start`), Playwright (screenshots, interaction), Chrome DevTools (console, network, performance traces, Lighthouse), and Figma (`https://mcp.figma.com/mcp`: `get_design_context` to read designs, `generate_figma_design` to send running UI back to canvas; signs in on first use). Servers that can't connect (Supabase not started, Figma not signed in) log an error at startup and are skipped.
- The design loop OpenAI and Figma recommend: read the Figma selection, build with your design-system components, then verify in a real browser against the screenshots at each breakpoint (`visual-review`), not just a passing build. Never point Supabase MCP at a hosted project without a human.
- `codex mcp add` writes to your user config instead, if the project config isn't picked up.

## Plugins
- A Codex plugin bundles skills (and optionally MCP servers/hooks) with a `.codex-plugin/plugin.json`; a repo marketplace lives at `.agents/plugins/marketplace.json`.
- `codex plugin marketplace add mj2tang/web-agent-playbook` registers this repo's marketplace.
- Plugin hooks run only after the user trusts them.

## Evaluating skills
- Start with 10–20 prompts per skill: explicit (names the skill), implicit (describes the task), noisy, and **negative** look-alikes that must not trigger it.
- Capture `codex exec --json` traces and write deterministic checks (did command X run, does file Y exist); add a model-graded rubric only for qualitative conventions.
- Turn every manual correction into a new eval case. See [`evals/skill-routing.jsonl`](../evals/skill-routing.jsonl).
