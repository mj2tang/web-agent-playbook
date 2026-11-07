---
name: web-quality-gates
description: The gates a web change must pass and what each one catches - make check (eslint, tsc, vitest), make db-check (migrations from zero, pgTAP, RLS on every table, type drift), make ui-check (Playwright e2e, axe, screenshots), make perf (Lighthouse budgets) - with the rule that SKIPPED is never a pass and gates, budgets, and snapshots are never edited to get green. Use when deciding which gates a change needs, when a gate fails, or when reviewing a branch. Not for choosing test cases - see tdd-loop.
---

# Web quality gates

| Gate | Command (no Makefile: `scripts/gates/…`) | Catches |
|---|---|---|
| check | `make check` / `check.sh` | lint errors, type errors, unit regressions (the starter's `check` also runs design-check) |
| design-check | `make design-check` / `design-check.sh` | raw colours and sizes instead of tokens, default-palette classes, the purple-gradient AI look, emoji as icons, removed focus outlines, clickable divs, raw `<img>`; plus Impeccable's detector (`npx impeccable detect`) when installed |
| db-check | `make db-check` / `db-check.sh` | migrations that don't apply from zero, broken policies, tables without RLS, generated types out of date |
| ui-check | `make ui-check` / `ui-check.sh` | broken pages and journeys, a11y violations (axe serious/critical), visual regressions at 3 widths |
| perf | `make perf` | LCP/CLS/INP and JS budgets from `configs/gates.json` |

## Which gates
- Any change: `check`.
- `supabase/` or `src/lib/contracts/` changed: + `db-check`.
- Pages, components, styles, or tokens changed: + `design-check` and `ui-check`.
- New route, client component, image, font, or third-party script: + `perf` when configured.

## Rules
- **SKIPPED is not a pass.** The gate scripts exit 4 when they skip (missing tool, script, or config). Report it, and the supervisor treats it as a finding until a human accepts the gap (`GATES_ALLOW_SKIP=1`).
- **Thresholds live in `configs/gates.json`** (axe impacts, screenshot diff ratio, Lighthouse budgets); the Playwright config and the a11y spec read it, and `make perf` generates its Lighthouse config from it.
- **Baselines are committed.** A missing screenshot baseline fails `ui-check`; only a human runs `make baselines`.
- **`design-lint-ignore: <reason>`** silences one line and needs a reason; reviewers read every one.
- **Never edit to get green:** `configs/gates.json`, snapshot files, axe rule disables, `test.skip`, `eslint-disable`, and `@ts-expect-error` added to pass are review findings. The guard hook protects gates and snapshots.
- **Run gates in the worker's checkout** (`make -C <worktree> ...`), on the committed HEAD.
- A flaky e2e test is a bug: fix the race (web-first assertions, no fixed sleeps), don't retry it into green.

## Done when
Every gate the change needs reports pass on the branch HEAD, with output pasted.
