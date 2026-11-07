---
name: visual-review
description: Check that built UI matches its component spec and the design tokens by taking screenshots at 375, 768, and 1280 widths in light and dark mode, in every specified state, and comparing them to the spec and to committed snapshots. Use after building or changing any page or component, and when reviewing a UI branch. Not for backend-only changes, and never to update snapshots without human approval.
---

# Visual review

Tests prove behaviour; screenshots prove it looks right. Look at them - don't just generate them.

## Procedure
1. **Start the app** on this branch's HEAD (`pnpm build && pnpm start`, or `pnpm dev` for quick iterations) with local Supabase seeded.
2. **Capture:**
   - Interactive: the Playwright MCP server (`browser_navigate`, `browser_resize`, `browser_take_screenshot`) for exploratory checks.
   - Committed: `pnpm exec playwright test --grep @visual` - specs in `tests/e2e/visual.spec.ts` run on the `mobile` (375), `tablet` (768), and `desktop` (1280) projects with `toHaveScreenshot()`.
3. **Cover states** from the component spec: hover, focus-visible, empty, error, loading, long content, signed out/in, and dark mode (`page.emulateMedia({ colorScheme: 'dark' })`).
4. **Compare against the spec,** item by item: spacing and alignment on the token scale, type sizes and weights, colours from tokens, truncation, alignment of baselines, nothing overlapping or clipped, focus ring visible.
5. **Report** each mismatch as `[severity] screenshot - expected (spec line) - actual - likely file:line`.

## Snapshots
- A failing `toHaveScreenshot` is a finding, not a chore. Fix the UI, or - if the change is intended - say so and **ask a human** to run `pnpm exec playwright test --update-snapshots`. The guard hook asks before that command; snapshot files are protected from agent edits.
- Mask genuinely dynamic regions (dates, avatars) with `mask:`, never by raising `maxDiffPixelRatio`.

## Done when
Screenshots exist for every specified state at three widths and both themes, and every difference from the spec is fixed or filed.
