---
name: design-brief
description: Turn a vague "make it look good" into a one-page design brief - audience, the job of each page, tone in three words, references the owner loves and hates, constraints, and what would make them wince - before any tokens or components exist. Use at the start of a new site, a redesign, or any page whose look isn't already defined by the design system. Not for changes inside an existing, documented design system - use component-spec.
---

# Design brief

A design system without a brief converges on the generic default. The brief is what makes this site look like *this* site.

## Procedure
1. **Ask, don't assume.** Get from the owner (or the epic):
   - Who lands here, from where, on what device, and what they must do in the first 10 seconds.
   - The one action each page exists for (primary CTA), and the secondary one.
   - Tone in three adjectives, plus one adjective it must **not** be.
   - 2-3 reference sites they love (and why: type, density, motion, photography) and 1-2 they dislike.
   - Hard constraints: brand colours/fonts that already exist, legal copy, languages, accessibility commitments.
2. **Write `docs/design/brief.md`** from `assets/design-brief-template.md`. Keep it to one page.
3. **Derive direction, not pixels:** type pairing (one display, one text face), colour strategy (one accent + neutrals, or a richer palette and why), density (airy marketing vs dense app), shape language (radius, borders vs shadows), motion stance (none / subtle / expressive).
4. **Show two directions** when the owner is unsure: two quick static mockups of the same hero/section in different directions, side by side. Let them pick or mix; record the choice in the brief.
5. **Hand off** to `design-tokens`.

## Done when
`docs/design/brief.md` exists, every template field is filled or marked "n/a - why", and the owner's chosen direction is recorded.
