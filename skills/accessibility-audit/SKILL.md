---
name: accessibility-audit
description: Audit and fix accessibility to WCAG 2.2 AA - automated axe scan (zero serious/critical), keyboard-only walkthrough, visible focus, semantic landmarks and headings, labels and errors on forms, colour contrast, target size, reduced motion, and screen-reader names - with evidence per page. Use for any UI change before review, when the a11y-reviewer asks, or for an audit of existing pages. Not for backend-only changes.
---

# Accessibility audit (WCAG 2.2 AA)

## Automated
- `make ui-check` runs `@axe-core/playwright` on every route in `tests/e2e/a11y.spec.ts`. Gate: **zero `serious` or `critical` violations**. Add new routes to that spec in the same change.
- Run axe in both themes and in each meaningful state (menu open, dialog open, form with errors).

## Manual (axe catches ~40%)
1. **Keyboard only:** Tab through the page. Every interactive element is reachable, in a logical order, with a visible focus ring (`--color-focus`, ≥3:1 against its background, not hidden by sticky headers - WCAG 2.4.11). Esc closes overlays and focus returns to the trigger.
2. **Structure:** one `h1`, no skipped heading levels, landmarks (`header`, `nav`, `main`, `footer`), a skip link to `main`.
3. **Names:** every button/link has an accessible name that makes sense out of context ("Delete note 'Groceries'", not "Delete"). Icon-only buttons have `aria-label`. Images: meaningful `alt` or `alt=""` if decorative.
4. **Forms:** visible `<label>` for each input, errors linked with `aria-describedby`, `aria-invalid` on invalid fields, error summary focused on submit, no placeholder-as-label, `autocomplete` attributes.
5. **Contrast:** text 4.5:1 (3:1 for ≥24px or ≥18.66px bold), UI components and graphics 3:1.
6. **Targets:** ≥24×24 CSS px or enough spacing (2.5.8). Dragging has a single-pointer alternative (2.5.7).
7. **Motion:** animations respect `prefers-reduced-motion`; nothing flashes >3 times/sec; auto-playing motion can be paused.
8. **Dynamic content:** async results announced via `aria-live="polite"`; loading states have text, not just spinners.
9. **Zoom:** usable at 200% zoom and 320px width without loss of content (1.4.10).

## Report
Per page: axe result, keyboard pass/fail with notes, issues as `[severity] file:line - WCAG criterion - problem - fix`.

## Done when
axe is clean on every changed route and the manual checklist passes or each failure is filed with a fix.
