### Bug fix

**You own the root cause and the evidence.** Every shipped line traces to something you observed. A change that "might help" is a hypothesis, not a fix, and it doesn't ship.

1. Reproduce it yourself on the surface where it was reported: the page in a real browser (Playwright, Playwright/DevTools MCP), the server action with `curl`, the policy with `psql` as the right role. Ask the user only after driving the surface as far as it goes, with a specific reason. If it won't reproduce, tighten the conditions or add logging until it does.
2. Narrow the cause by elimination: list the hypotheses (see the web suspects in skill `systematic-debugging`), then rule them out with evidence, biggest split first. When state is unclear, log it and read it as the code runs.
3. Write the failing test that captures the repro (Playwright for UI, pgTAP for data access, Vitest for logic) (skill `tdd-loop`). Commit it before the fix.
4. Fix at the first place it went wrong (Fix root causes). If the fix crosses the contract, stop: that's a task for the system-architect.
5. Verify on the same surface: the original repro now passes, and the test you wrote fails without the fix. Run the gates the change needs (skill `web-quality-gates`).
6. If two fixes on the same assumption failed, write the assumption down and test it directly (Attack the premise).
7. Record the lesson (skill `encode-lesson`): a test or lint if it can recur, a `docs/solutions/` note if it's a trap no check can hold.

**Reply:** what was broken and for whom, the root cause, the fix, and the failing-then-passing output pasted verbatim.
