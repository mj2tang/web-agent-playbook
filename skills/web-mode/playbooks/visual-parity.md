### Visual parity

**You own pixel-exact equivalence.** The baseline is the spec, and you don't touch it. Parity is proven by image diff, not by eye.

1. Baseline first: screenshot the current implementation in every state, width (375/768/1280), and theme with Playwright `toHaveScreenshot` (skill `visual-review`). No baseline, no parity claim. Writing the baselines is a human-approved step (`make baselines`).
2. Hold the line: no edits to baselines, the screenshot harness, or diff thresholds to make a diff pass. If a baseline looks wrong, stop and ask.
3. Migrate one component at a time, shared primitives first. Parallel work gets one owner per component in separate worktrees.
4. Verify each component against its baseline. Any non-zero diff is a fail: open the diff image, find the pixel delta, fix, repeat until zero.
5. Run the gates (skill `web-quality-gates`); design-check catches raw values sneaking in during a styling migration.

**Reply:** components migrated, the diff result for each, where the baselines live, and what's left.
