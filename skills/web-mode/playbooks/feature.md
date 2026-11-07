### Feature

**You own the design and the proof.** Build from a named data shape.

1. Read the context: `PRODUCT.md`, `DESIGN.md`, the component specs, `docs/design/system.md`, and `docs/solutions/` for this area.
2. Name the data shape: props and states for UI (skill `component-spec`), tables, policies, and Zod schemas for data (skill `api-contract`). If the contract has to change, that's wave 0 for the system-architect.
3. Write the throughput check as four todo items (each can be `n/a: <reason>`): what must happen first, which parts are independent (frontend vs backend, disjoint files), what's shared (tokens, types, migrations - one owner), and whether one worker is simply best.
4. Build test-first in small verifiable units (skill `tdd-loop`): each ends with a passing check and a commit. Every state from the spec: empty, loading, error, long content, signed out.
5. Verify on the matching surface (skill `prove-it-works`): the pages in a browser at 375/768/1280 and both themes (skill `visual-review`), the actions with and without a session, the data as another user. Run the gates (skill `web-quality-gates`).
6. If the design is contested or the change touches auth or RLS, run a cross-model review (skill `interrogate`).

**Reply:** what users can now do, the data shape you chose and why, the throughput check, the evidence, and open decisions (a table when there were alternatives).
