---
name: component-spec
description: Specify a component or page section before it is built - purpose, anatomy, variants, every state (default, hover, focus-visible, active, disabled, loading, empty, error), responsive behaviour, keyboard and screen-reader behaviour, and the tokens it uses - in docs/design/components/<name>.md. Use before a worker builds any new component or page, or when a component's behaviour is disputed. Not for trivial markup changes to an already-specified component.
---

# Component spec

## Procedure
1. **Search first:** is there an existing component that does this with a new variant? Prefer a variant over a new component.
2. **Write `docs/design/components/<name>.md`** with:
   - **Purpose:** one sentence; where it is used.
   - **Anatomy:** named parts (e.g. card → media, title, meta, actions).
   - **Props/variants:** name, type, default. Keep variants orthogonal (`size` × `tone`), not one-off combinations.
   - **States:** default, hover, focus-visible, active, disabled, loading (skeleton or spinner and where), empty (copy + action), error (copy + recovery). Each state names its tokens.
   - **Responsive:** behaviour at <640, 640-1024, >1024 (stack, wrap, truncate, hide - never hide essential actions).
   - **Accessibility:** element/role, accessible name, keyboard map (Tab, Enter/Space, Esc, arrows), focus management, `aria-live` for async updates.
   - **Content rules:** max lengths, truncation, long-word/RTL behaviour.
3. **Acceptance:** list the Playwright checks a worker must write (role locators, each state reachable, axe clean, screenshot names for `visual-review`).

## Done when
Every state has a defined look and copy, and the spec names the tests and screenshots that prove it.
