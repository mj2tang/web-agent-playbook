### Perf issue

**You own the measurement.** Every fix is tied to a before and after number; reading source is not measuring.

1. Capture a baseline on the real surface: `make perf` (Lighthouse), a Chrome DevTools performance trace (DevTools MCP), `pnpm build` route sizes, or `explain analyze` as `authenticated` for a query. Vet the number before trusting it (skill `frontend-performance`, Explain the number).
2. Find what limits it from the trace, then try the cheapest fix first: don't do the work at all, don't do it twice, do less, do it later (lazy, streaming), do it off the critical path, then make it cheaper.
3. Change one thing at a time and re-measure after each; keep only changes that move the number.
4. Compare the artifacts side by side (before/after JSON or traces). "Inconclusive" is not a win.
5. Run the gates (skill `web-quality-gates`); a faster page that fails axe or the screenshots isn't done.

**Reply:** the baseline, the result, the delta, what limited it, and the artifact paths.
