---
name: web-mode
description: Rigorous mode for a web task - restate the goal and the smallest change, match the task to a playbook (investigation, bug fix, feature, refactoring, prototype, visual parity, perf issue, team), copy its steps into the todo list, apply the principles index, and finish with an evidence-labelled reply. Use when the user types web-mode or $web-mode, or asks to work rigorously on a web task. Not invoked automatically; for a quick, fully specified edit just do it.
disable-model-invocation: true
---

# Web mode

The entry point for rigorous web work. It picks the playbook, the playbook calls the other skills. After Lauren Tan's pstack (`poteto-mode`): go deep on one agent until you can trust it, and parallelism follows.

## First, every time
1. **Say back the goal** in your own words: who it's for, the problem, and the smallest change you expect to meet it. Don't wait for confirmation. If the evidence rules out what was asked, show that and stop. Repeat the goal at the top of every subagent brief and every final reply.
2. **Pick the playbook** below and open a todo list whose first items are its steps, copied verbatim. A step you skip stays in the list as `skip: <reason>`.
3. **Read the principles** that apply (index below). In the reply, name each one that changed a decision and what it changed.

## Rules that apply in every playbook
- **Name the data shape before code.** Component props and states, the table and its policies, the Zod schema. Pick the structure that holds it (a state machine over loose booleans, a lookup table over branching).
- **Forks you can observe aren't questions.** "Which layout?", "is this faster?", "does this fix it?" are settled by building a throwaway (Prototype playbook) or running a measurement. Ask the human only about taste, product, or brand calls no experiment can settle, and irreversible actions.
- **Prove it on the same surface.** A UI bug is fixed when the browser shows it fixed (Playwright or the Playwright/DevTools MCP), not when a unit test passes. "Inconclusive" or "checked somewhere else" is not a pass.
- **Every claim carries its label.** Measured (with the artifact), inferred (from what), or a guess. Never hand the human a check you could run yourself.
- **You own your subagents' work.** Read their diff and evidence and write your own summary. For a fix round or follow-up, start a fresh subagent with the consolidated scope (original brief, every later instruction, the previous report, the branch) instead of resuming a stale one.
- **No is an acceptable answer.** If an approach or extra scope doesn't earn its place, say so.
- **Comments only for a non-obvious why.** No phase narration in code or tests; the assertion message documents the step.

## Principles
Short rules; each names when it applies. After pstack's principle set, adapted for web work.

**Core**
- **Smallest change.** Sizing any diff: prefer deletion and the least code that solves it; no new layers "for later".
- **Subtract before you add.** Before building: remove dead components, unused tokens, stale flags; then build on the simpler base.
- **Data shape first.** Before logic: the props, state, table, and schema decide how simple the rest is.
- **Build the lever.** Repeated or checkable work (renames across routes, auditing every page, migrating styles): write the codemod, script, or test that does or proves it. The script is what a reviewer reruns.
- **Experience first.** Product and UX trade-offs: fewer polished states over more rough features; the empty, loading, and error states are part of the feature.
- **Exhaust the design space.** A new interaction or layout with no precedent: build 2-3 throwaway variants behind a switcher and compare screenshots before committing.
- **Attack the premise.** Two fixes sharing one assumption failed the same gate: write the assumption down and test it directly before a third fix.

**Architecture**
- **Boundaries hold the guards.** Validate with Zod at server actions, route handlers, and forms; check auth there and in RLS; trust typed data inside.
- **Model the domain.** Branchy UI state (wizards, async flows): a state machine or reducer, not scattered booleans.
- **Make operations idempotent.** Server actions, webhooks, migrations, seeds: running twice ends in the same state.
- **Migrate callers, then delete.** Replacing a component or API: move every caller and delete the old one in the same change; no compatibility shims.

**Verification**
- **Prove it works** (skill `prove-it-works`). Before done: the real page, the real query, the real response.
- **Fix root causes.** Debugging: find the first place it went wrong; a guard is a fix only if the state it handles is legitimate.
- **Verifiable units.** Multi-step work: small units that each end in a passing check, committed in an order that proves itself (failing test, then fix).
- **Test behaviour, not implementation.** Assert what users see (roles, text, URL, visible state), not component internals.
- **Explain the number.** Any measured number (LCP, bundle size, query time, axe count): find what limits it and rule out measuring the wrong thing before you report or act on it (`frontend-performance`).

**Delegation**
- **Guard the context window.** Big outputs, logs, traces, many files: send them to a subagent and keep its summary.
- **Never block on the human.** Reversible work: do it, show it, let them correct. Pause only for the irreversible list in `AGENTS.md`.

**Meta**
- **Encode lessons in structure** (skill `encode-lesson`). Writing the same instruction twice: make it a test, lint, schema, or hook instead.

## Playbooks
Match the task, open the file, copy its steps.

- **Investigation** (`playbooks/investigation.md`): a read-only question - how does X work, why is Y built this way, are we sure, X or Y?
- **Bug fix** (`playbooks/bug-fix.md`): a reported defect to reproduce, root-cause, and fix with evidence on the same surface.
- **Feature** (`playbooks/feature.md`): new or changed behaviour, built from a named data shape.
- **Refactoring** (`playbooks/refactoring.md`): a behaviour-preserving change to structure.
- **Prototype** (`playbooks/prototype.md`): a throwaway to decide a design or settle an observable fork.
- **Visual parity** (`playbooks/visual-parity.md`): pixel-exact match between two implementations, or a styling migration.
- **Perf issue** (`playbooks/perf-issue.md`): a measured slowness, improved against a baseline.
- **Team** (`playbooks/team.md`): an epic with several independent features - hand it to the orchestrator.

No playbook fits? Write a short bespoke one in the same shape (owner line, numbered steps, reply), show it, and follow it.

## The reply
Short declarative sentences. Lead with who the change is for and what changes for them, then what the next maintainer inherits. Every claim labelled measured / inferred / guess, with the artifact path or link. End with what's open and what needs a human.
