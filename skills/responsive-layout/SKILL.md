---
name: responsive-layout
description: Build layouts mobile-first that hold from 320px to wide desktop - fluid containers, CSS grid/flex with intrinsic sizing, container queries for components, fluid type with clamp(), 24px+ touch targets, no horizontal scroll - and verify at 375, 768, and 1280 widths. Use when creating or changing any page layout, grid, navigation, or component that must adapt to screen size. Not for print styles or native apps.
---

# Responsive layout

## Rules
- **Mobile-first:** base styles for the narrowest screen; add `sm:` / `md:` / `lg:` (or `min-width` queries) upward.
- **Intrinsic before breakpoints:** `grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr))`, `flex-wrap`, `max-width: 65ch` for prose. Breakpoints only where content breaks.
- **Components respond to their container** (`@container`), pages to the viewport.
- **Fluid type and space:** `clamp()` between token sizes for display text; body text never below 16px.
- **Touch:** targets ≥ 24×24 CSS px (44×44 for primary actions), 8px between adjacent targets.
- **No horizontal scroll** at 320px. Long words/URLs: `overflow-wrap: anywhere`. Tables: scroll inside their own container with a visible affordance.
- **Navigation:** visible primary nav on desktop; on mobile, a disclosure button with `aria-expanded`, focus trapped only in true modals.
- **Media:** `next/image` with `sizes`; aspect-ratio boxes to prevent layout shift.
- **Safe areas:** `env(safe-area-inset-*)` for fixed bars.

## Verify
Screenshots at 375, 768, 1280 (`visual-review`) plus a manual 320px pass: `await page.setViewportSize({ width: 320, height: 800 })` and assert `document.documentElement.scrollWidth <= 320`.

## Done when
No horizontal overflow at 320, screenshots at three widths match the component spec, and touch targets meet the size rule.
