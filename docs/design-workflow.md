# Design workflow

From "make it look good" to a shipped, accessible UI.

1. **Brief** (`design-brief`): audience, the job of each page, three tone words plus one it must not be, references loved and hated, what would make the owner wince. Written to `PRODUCT.md` (who and what) and `DESIGN.md` (direction, do/don't) at the repo root - the same files Impeccable and gstack use, so those tools stay on brief too. When the owner is unsure, show two directions side by side.
2. **Tokens** (`design-tokens`): semantic colour, type, space, radius, shadow, and motion in `src/styles/tokens.css`, light and dark, contrast-checked, mapped into Tailwind's `@theme`. No raw values in components.
3. **Component specs** (`component-spec`): anatomy, variants, every state (hover, focus-visible, disabled, loading, empty, error), responsive behaviour, keyboard and screen-reader behaviour, and copy (`ux-copy`).
4. **Build** (frontend-worker): server components by default, tokens only, every state, role-based Playwright tests.
5. **Check:**
   - `responsive-layout`: no horizontal scroll at 320px; screenshots at 375/768/1280.
   - `accessibility-audit`: axe with zero serious/critical issues on every route in both themes, plus a keyboard-only pass.
   - `visual-review`: compare screenshots to the spec; snapshots change only with human approval.
   - `frontend-performance`: route JS and Core Web Vitals within `configs/gates.json`.

## Specialist skills that pair well
Impeccable (audit and polish with an anti-pattern library), Anthropic's `frontend-design` (distinctive new pages), and Vercel's `web-design-guidelines` (UI audit with `file:line` findings) add taste and rules on top of this workflow; install commands are in the README. Keep the brief and tokens as the source of truth when their advice conflicts.

## From Figma
With the Figma MCP server (in `.codex/config.toml`; `claude mcp add` for Claude Code), the ui-designer reads a frame with `get_design_context`, maps it to existing tokens and components, and writes the component spec; workers build from the spec. `generate_figma_design` sends the running UI back to Figma for review.

## Avoiding the generic look
No default purple/blue gradient hero, no emoji as icons, no three identical feature cards as the only layout, one typeface pair chosen from the brief, real copy, and an accent used sparingly. Decide density, shape language, and motion in the brief, then hold to it.
