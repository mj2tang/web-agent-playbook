---
name: systematic-debugging
description: Debug by reproduction and evidence - reproduce, isolate, form ranked hypotheses, test them one at a time, then fix with a regression test. Use for any bug, failing test, broken page, RLS denial, or flaky e2e run, before proposing a fix. Not for feature work with no failing behaviour.
---

# Systematic debugging

1. **Reproduce** with a single command; save the output.
2. **Isolate:** smallest input / fixture / commit that shows the problem (`git bisect` for regressions).
3. **Hypothesise:** list 2–4 causes ranked by likelihood, each with the evidence that would confirm or reject it.
4. **Test** one hypothesis at a time (logging, assertions, a probe script). Record the result.
5. **Fix** the root cause, with a test that failed before and passes now.
6. After two failed fix attempts, stop and write up what you know instead of trying a third.

Web suspects: server vs client component boundary, stale `.next` cache or dev server, hydration mismatch (dates, random IDs), RLS silently returning zero rows (not an error), the query running as `anon` because the session cookie wasn't refreshed in the proxy (`src/proxy.ts`, formerly middleware), types generated before the last migration, a Playwright race (missing `await expect(...)`), and a dependency upgrade.
