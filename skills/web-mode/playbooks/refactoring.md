### Refactoring

**You own behaviour staying identical.** Structure changes; what users see doesn't.

1. Pin the behaviour first: Playwright tests and committed screenshot baselines must cover what users observe on every affected route. If coverage is thin, add characterisation tests and commit them before touching the code.
2. Subtract before you add: delete dead code, unused props and tokens, stale flags.
3. When many call sites change the same way, build the lever: a codemod or script, run it, and review its output, rather than editing by hand.
4. Migrate callers, then delete the old component or API in the same change. No compatibility shims.
5. Prove nothing changed: the same tests pass, screenshots match the committed baselines with zero diff (skill `visual-review`), and the gates are green (skill `web-quality-gates`).

**Reply:** what changed structurally and why it's simpler for the next maintainer, the codemod if any, and the unchanged-behaviour evidence (tests, zero screenshot diff).
