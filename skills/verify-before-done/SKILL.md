---
name: verify-before-done
description: Before claiming work is complete, run the project's verification commands and report actual output - lint, types, unit tests, database tests, accessibility, and visual checks. Use at the end of every task, before committing, and before opening a PR. Not needed for read-only questions.
---

# Verify before done

Run the checks and paste the real result, not what you expect:

```
make check      # eslint + tsc --noEmit + vitest
make db-check   # if supabase/ changed: db reset, pgTAP, RLS on every table, types up to date
make design-check  # if UI changed: tokens, focus, semantics, generic-AI patterns (part of check in the starter)
make ui-check   # if pages/components changed: Playwright + axe + screenshots
```
In repos without these make targets: `scripts/gates/check.sh`, `db-check.sh`, `design-check.sh`, `ui-check.sh`.

- Report each as pass / fail / **skipped (why)**. Skipped is not pass.
- If something fails, say so and fix it or report it - never say "should work".
- Look at the screenshots you produced; a passing test can still render a broken page.

For anything beyond a small edit, also follow `prove-it-works`: cover every affected entry point in `docs/pipeline-map/` and record the evidence.
