---
name: design-tokens
description: Create or extend the project's design tokens - semantic colour, type, spacing, radius, shadow, and motion as CSS custom properties in src/styles/tokens.css with light and dark sets, mapped into the Tailwind theme - and enforce that components use tokens, never raw hex or px. Use after a design brief exists, when adding a colour/size the system lacks, or when reviewing UI code for hard-coded values. Not for one-off layout tweaks that existing tokens already cover.
---

# Design tokens

Tokens are the contract between design and code. Workers style with tokens; only the ui-designer adds tokens.

## Procedure
1. **Read** `DESIGN.md` (and `PRODUCT.md`) and the existing `src/styles/tokens.css`.
2. **Define semantic tokens**, not palette names. Components say what a colour *means*:
   - Colour: `--color-bg`, `--color-surface`, `--color-fg`, `--color-muted`, `--color-border`, `--color-accent`, `--color-accent-fg`, `--color-danger`, `--color-success`, `--color-focus`.
   - Type: `--font-display`, `--font-text`, `--font-mono`; sizes `--text-xs` … `--text-4xl` on a modular scale; `--leading-*`.
   - Space: `--space-1` … `--space-16` on a 4px base (`--space-1: 0.25rem`).
   - Shape: `--radius-sm|md|lg|full`; `--shadow-sm|md|lg`.
   - Motion: `--duration-fast|base|slow`, `--ease-standard`; respect `prefers-reduced-motion`.
3. **Light and dark sets:** define defaults on `:root`, the dark set under `@media (prefers-color-scheme: dark)` scoped to `:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`.
4. **Map into Tailwind** (`@theme` in `src/app/globals.css`, Tailwind v4) so `bg-surface`, `text-muted`, `p-4`, `rounded-md` resolve to tokens.
5. **Check contrast** for every fg/bg pair you defined: 4.5:1 for text, 3:1 for large text, UI borders, and focus rings - in both themes.
6. **Update DESIGN.md's token summary** so other agents and tools see the system without reading CSS.
7. **Avoid the generic AI look:** no default purple/blue gradient hero, no emoji as icons, no three identical feature cards as the only layout, one typeface pair chosen from the brief, real copy instead of lorem ipsum, and an accent used sparingly.

## Rules for everyone else
- No raw hex/rgb/hsl or arbitrary `[13px]` values in components. Add a token (ask the ui-designer) instead.
- No new font families outside `--font-*`.

## Done when
`make design-check` (or `scripts/gates/design-check.sh`) reports 0 findings, and both themes pass the contrast check.
