---
name: frontend-performance
description: Keep pages fast against explicit budgets - LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms, and ≤ 170KB gzipped JS per route - using server components by default, next/image and next/font, streaming with Suspense, and measuring with Lighthouse CI (make perf) and the Next.js build output. Use when adding pages, client components, third-party scripts, large images, or fonts, or when a route exceeds its budget. Not for backend query tuning - see data-modeling.
---

# Frontend performance

Budgets live in `configs/gates.json` (`perf`); changing them needs a human.

## Defaults that keep you inside budget
- **Server components by default.** Add `"use client"` only to the leaf that needs state, effects, or browser APIs. Never at a layout or page root.
- **Images:** `next/image` with explicit `width`/`height` or `fill` + `sizes`; `priority` only on the LCP image; AVIF/WebP via the default loader.
- **Fonts:** `next/font` (self-hosted, `display: swap`, subset); at most two families, the weights you use.
- **Data:** fetch on the server, in parallel (`Promise.all`), stream slow parts with `<Suspense>` and a skeleton that reserves space (CLS).
- **Third-party scripts:** `next/script` with `strategy="lazyOnload"` or `afterInteractive`; each one is a budget line item.
- **Interactions:** keep handlers cheap; defer heavy work with `startTransition`; virtualise lists over ~200 rows.
- **Dependencies:** check the size before adding (`pnpm why`, bundle analyzer); prefer platform APIs and tree-shakeable imports.

## Measure
- `pnpm build` prints per-route "First Load JS" - compare to the budget.
- `make perf` runs Lighthouse CI against `pnpm start` with the assertions from `configs/gates.json`.
- In review, attach the before/after numbers for changed routes.

## Explain the number (before you report or act on it)
After pstack's benchmark checklist. A number you can't explain is a guess.
- **What limits it?** From the trace: the LCP element and what delays it (server time, render-blocking CSS/JS, image size, font), long tasks for TBT/INP, what shifts for CLS.
- **Same conditions?** Production build (`pnpm build && pnpm start`), same throttling and device profile, cold vs warm cache stated, same data (seeded, same row counts). Dev-server numbers don't count.
- **Repeat it.** At least 3 runs; report the median and the spread. A delta smaller than the spread is noise.
- **Errors and empty pages?** A fast page that rendered an error or no data measured the wrong thing; check the screenshot and console.
- **Does it matter end to end?** A faster component that isn't on the critical path doesn't move LCP; say which user-visible metric moved.

## Cheapest fix first
Don't do the work at all → don't do it twice (cache, dedupe fetches) → do less (smaller images, fewer fonts, less JS) → do it later (lazy load, stream with Suspense) → do it off the critical path → make it cheaper. Stop at the first one that meets the budget.

## Done when
Every changed route is within the JS budget in the build output, and `make perf` (when configured) passes.
