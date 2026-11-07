---
name: design-brief
description: Turn a vague "make it look good" into the two design context files every UI agent reads - PRODUCT.md (audience, the job of each page, constraints, what would make the owner wince) and DESIGN.md (tone, type, colour strategy, density, shape, motion, do and don't) - at the repo root, before any tokens or components exist. Use at the start of a new site, a redesign, or any page whose look isn't already defined. Not for changes inside an existing, documented design system - use component-spec.
---

# Design brief → PRODUCT.md + DESIGN.md

A design system without a brief converges on the generic default. These two files make this site look like *this* site. They sit at the repo root because Impeccable (`$impeccable init` / `document`), gstack (`/design-consultation`), and similar tools read and write the same names, so every agent stays on brief.

## Procedure
1. **Ask, don't assume.** Get from the owner (or the epic):
   - Who lands here, from where, on what device, and what they must do in the first 10 seconds.
   - The one action each page exists for (primary CTA), and the secondary one.
   - Tone in three adjectives, plus one adjective it must **not** be.
   - 2-3 reference sites they love (and why: type, density, motion, photography) and 1-2 they dislike.
   - Hard constraints: brand colours/fonts that already exist, legal copy, languages, accessibility commitments.
2. **Write `PRODUCT.md`** from `assets/PRODUCT-template.md`: who it's for, what it must do, constraints. One page.
3. **Write `DESIGN.md`** from `assets/DESIGN-template.md`: the direction, not pixels - type pairing (one display, one text face), colour strategy (one accent + neutrals, or a richer palette and why), density, shape language (radius, borders vs shadows), motion stance, imagery, and a short **do / don't** list drawn from the references.
4. **Show two directions** when the owner is unsure: two quick static mockups of the same hero in different directions, side by side. Let them pick or mix; record the choice in DESIGN.md's decision log.
5. **Hand off** to `design-tokens`, which turns DESIGN.md into `src/styles/tokens.css` and keeps DESIGN.md's token summary current.

## Existing files
If PRODUCT.md or DESIGN.md already exist (written by you, the owner, or another tool), update them in place - keep their sections, add missing ones - rather than starting over.

## Done when
PRODUCT.md and DESIGN.md exist at the repo root, every template field is filled or marked "n/a - why", and the owner's chosen direction is in DESIGN.md's decision log.
