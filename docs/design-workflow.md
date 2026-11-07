# Design workflow

From "make it look good" to a shipped, accessible UI.

1. **Brief** (`design-brief`): audience, the job of each page, three tone words plus one it must not be, references loved and hated, what would make the owner wince. One page in `docs/design/brief.md`. When the owner is unsure, show two directions side by side.
2. **Tokens** (`design-tokens`): semantic colour, type, space, radius, shadow, and motion in `src/styles/tokens.css`, light and dark, contrast-checked, mapped into Tailwind's `@theme`. No raw values in components.
3. **Component specs** (`component-spec`): anatomy, variants, every state (hover, focus-visible, disabled, loading, empty, error), responsive behaviour, keyboard and screen-reader behaviour, and copy (`ux-copy`).
4. **Build** (frontend-worker): server components by default, tokens only, every state, role-based Playwright tests.
5. **Check:**
   - `responsive-layout`: no horizontal scroll at 320px; screenshots at 375/768/1280.
   - `accessibility-audit`: axe with zero serious/critical issues on every route in both themes, plus a keyboard-only pass.
   - `visual-review`: compare screenshots to the spec; snapshots change only with human approval.
   - `frontend-performance`: route JS and Core Web Vitals within `configs/gates.json`.

## Avoiding the generic look
No default purple/blue gradient hero, no emoji as icons, no three identical feature cards as the only layout, one typeface pair chosen from the brief, real copy, and an accent used sparingly. Decide density, shape language, and motion in the brief, then hold to it.
