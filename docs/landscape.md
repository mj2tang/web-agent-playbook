# Landscape: what we took from the most popular agent playbooks

Star counts from the GitHub API on 2026-11-08 (pstack: the `cursor/plugins` repo it lives in). All content here is original; these projects shaped the ideas.

| Repo | Stars | Its core idea | What this playbook took |
|---|---|---|---|
| [Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack) (in `cursor/plugins`, 15.7k; ports such as `michael-denyer/pstack-claude` 4.1k, `backnotprop/pstack` 3.8k) | Go deep on one agent until you trust it, then parallelise. `poteto-mode` routes each task to one of 23 playbooks whose steps are copied into the todo list, with an inline index of 24 one-line principles; `blast-radius`, `benchmark-checklist`, `interrogate`, `show-me-your-work`, `create-verification-skill` (feature map) | The ML sibling already had `prove-it-works`, `encode-lesson`, `interrogate`, the decision trail, the trust ladder, and the pipeline map. New here: `web-mode` (8 web playbooks, steps copied verbatim, skips with a reason, principles index, say-back-the-goal, evidence labels, observable forks settled by prototypes), `blast-radius` for web dependencies, "explain the number" in `frontend-performance`, and fresh workers with consolidated scope in `orchestrate-team` |
| [obra/superpowers](https://github.com/obra/superpowers) | 314k | Mandatory gated workflow (brainstorm → plan → TDD → review → finish), bootstrap skill injected at session start, skills tested with an eval harness | Plan-first and TDD skills, "evidence before done", a fresh reviewer per branch, routing evals for every skill |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 299k | Harness optimisation: hook profiles, learned "instincts" with confidence scores, a memory vault, a security scanner, context budgets | `doctor`; hook profiles stay simple (guardrails on or off); learning goes to tests first, then `docs/solutions/` |
| [anthropics/skills](https://github.com/anthropics/skills) | 189k | The Agent Skills format; `frontend-design` | SKILL.md format; recommended alongside our design skills |
| [github/spec-kit](https://github.com/github/spec-kit) | 148k | Constitution → specify → plan → tasks → implement → converge | Frozen `EPIC.md` + checkable exit condition; the contract freeze is our "constitution" for data and APIs |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 147k | A searchable design database (styles, palettes, font pairings, per-industry anti-patterns) that generates `MASTER.md` plus per-page overrides, and a pre-delivery checklist | The pre-delivery checklist became deterministic `design-check` rules (no emoji icons, focus kept, contrast, breakpoints); one design context file at the root |
| [garrytan/gstack](https://github.com/garrytan/gstack) | 141k | Opinionated roles as commands: CEO/design/eng plan reviews with 0-10 scores, QA lead with a real browser, ship, canary, retro; Codex as a second opinion | `design-critique` (0-10 per dimension + "what a 10 looks like"); `DESIGN.md`; cross-model review (`interrogate`) |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 114k | 25 lifecycle skills (define → plan → build → verify → review → ship), 4 reviewer personas, native Codex plugin | Lifecycle coverage check; `frontend-performance`, `security-review`, and `observability` cover the same ground for web |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 105k | Design vocabulary commands (polish, bolder, critique, audit), `PRODUCT.md` + `DESIGN.md`, and a **deterministic 62-rule anti-pattern detector** that runs as a hook | `PRODUCT.md` + `DESIGN.md` at the root (shared with Impeccable); `design-check` runs `impeccable detect` when installed, next to our own rules |
| [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | 55k | Agile roles (analyst, PM, architect, scrum master, dev, QA) handing off documents | Role handoffs through files (`docs/design/system.md`, task files), not chat |
| [wshobson/agents](https://github.com/wshobson/agents) | 42k | Large catalogue of plugins, agents, and commands across harnesses | Kept our team small (9 roles); specialists are skills, not more agents |
| [Yeachan-Heo/oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex) | 34k | Codex-native hooks, tmux agent teams with per-worker worktrees, a HUD, mission ledgers, `omx doctor` | Codex hooks and native agents; worktree-per-worker (`run-wave.sh`); `doctor` |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 34k | `react-best-practices`, `web-design-guidelines` (UI audit with `file:line` findings) | Recommended in "Pairs well with"; `file:line` findings format in our linters and reviewers |
| [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) | 26k | Plan → work → review → **compound**: learnings in `docs/solutions/` that the next plan reads | `docs/solutions/` written by `encode-lesson`, read by `plan-first`, `feature-spec`, and `system-design-doc` |

## Patterns most of them share
1. **Plan before code, with a human gate** (superpowers, spec-kit, BMAD, compound-engineering, gstack). Here: `plan-first`, `EPIC.md`, and the contract freeze.
2. **Evidence over claims** (superpowers verification, gstack QA with replayable evidence, OMX checkpoints). Here: `prove-it-works`, the pipeline map, the decision trail, and gates that exit non-zero on SKIPPED.
3. **Design context in files** (Impeccable, gstack, ui-ux-pro-max). Here: `PRODUCT.md`, `DESIGN.md`, tokens, and component specs.
4. **Deterministic checks for taste problems** (Impeccable's detector, ui-ux-pro-max's checklist). Here: `design-check`.
5. **Learning that compounds** (compound-engineering, ECC instincts). Here: `encode-lesson`, which reaches for a test, schema, lint, or hook first and a `docs/solutions/` note second.
6. **Cross-harness packaging** (almost all ship Claude Code + Codex). Here: one `skills/` folder, Claude subagents plus generated Codex agents, and one guard for both hook systems.

## What we deliberately left out
- **Session-start bootstrap injection** (superpowers, ECC): `AGENTS.md` already routes to the skills, and both harnesses load it every session.
- **Learned-instinct scoring and memory vaults** (ECC): state lives in files a reviewer can read (task board, decision trail, `docs/solutions/`).
- **Dashboards / HUDs** (OMX): `tasks/BOARD.md` and `audit.py` cover visibility without a tmux dependency.
- **Deploy, canary, and land automation** (gstack): deploys stay a human step in this playbook.
- **Large data catalogues of styles and palettes** (ui-ux-pro-max): we keep the brief and tokens project-specific and recommend that skill for exploration.
