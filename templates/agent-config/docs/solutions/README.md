# Solutions — what this project has learned

Problems that cost real time, written so the next agent doesn't pay for them again. Planning reads this folder
before writing a plan or task (`plan-first`, `feature-spec`, `system-design-doc`); `encode-lesson` writes to it.

**A test, schema, lint rule, or hook beats a note.** Write a solution only for what can't be enforced (a
third-party quirk, a misleading error message, a design decision that keeps getting re-argued), or link the
mechanism you added from the note so people know why it exists. After compound-engineering's `docs/solutions/`.

One file per problem: `docs/solutions/<area>-<short-slug>.md` (areas: `auth`, `rls`, `migrations`, `ui`,
`a11y`, `perf`, `deploy`, `tooling`, `codex`, ...). Find relevant ones with `grep -ril <keyword> docs/solutions`.

## Template

```markdown
# <symptom, in the words someone would search for>

- Area: <auth | rls | migrations | ui | a11y | perf | deploy | tooling | ...>
- Seen: <date>, <task or PR>

## Symptom
<what you saw: error text, wrong behaviour, screenshot>

## Root cause
<why it happened>

## Fix
<what fixed it; the commit>

## Prevention
<the test, schema, lint, or hook that now catches it - or why none is possible>

## How to spot it next time
<the clue that should make an agent open this file>
```
