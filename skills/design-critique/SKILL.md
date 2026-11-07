---
name: design-critique
description: Score a UI or a UI plan 0-10 on each design dimension (hierarchy, typography, colour, spacing and rhythm, states, copy, accessibility, responsiveness, distinctiveness), say concretely what a 10 would look like for this project, and list the changes that close the biggest gaps - judged against PRODUCT.md and DESIGN.md, from screenshots, not code. Use before building a page from a plan, when the owner asks "is this good?", or as the ui-designer's review of a UI branch. Not for pass/fail gates - use design-check, accessibility-audit, and visual-review for those.
---

# Design critique (scored)

A score per dimension with "what a 10 looks like" turns taste into a to-do list. After gstack's plan-design-review and Impeccable's critique.

## Inputs
`PRODUCT.md`, `DESIGN.md`, the component specs, and **screenshots** of the page or plan (375/768/1280, light and dark - `visual-review` captures them). Judge what a user sees, not the code.

## Score each dimension 0-10
| Dimension | A 10 here means |
|---|---|
| Hierarchy | One obvious primary action per view; the eye lands where PRODUCT.md says the page's job is |
| Typography | The DESIGN.md pairing, a clear scale, comfortable measure (45-75ch), no orphaned headings |
| Colour | Tokens only, the accent used sparingly and on purpose, contrast passes in both themes |
| Spacing and rhythm | Consistent steps from the space scale; related things grouped, unrelated things separated |
| States | Empty, loading, error, long-content, and signed-out states designed, not defaulted |
| Copy | Specific buttons and errors in the DESIGN.md voice (`ux-copy`) |
| Accessibility | Keyboard path, visible focus, names that make sense out of context |
| Responsiveness | Each width looks designed, not squeezed; nothing essential hidden on mobile |
| Distinctiveness | Couldn't be mistaken for a template: no generic gradient hero, no emoji icons, no identical card rows |

For each: the score, one sentence of evidence (screenshot + where), and what a 10 would look like **for this project**.

## Output
```
DESIGN SCORE: <average>/10   (lowest: <dimension> <score>)
| Dimension | Score | Evidence | What a 10 looks like |
TOP CHANGES (biggest gap first, max 5):
1. <change> - <file or component> - raises <dimension> from x to y
TASTE QUESTIONS FOR THE OWNER: <only genuine preference calls>
```

## Rules
- Score against PRODUCT.md and DESIGN.md, not your own taste. If they're missing, say so and run `design-brief` first.
- Settle what's observable yourself; only taste calls (brand direction, tone) go to the owner.
- Re-score after changes; the trend is the point. Gates (design-check, axe, screenshots) still decide pass/fail.
