### Prototype

**You own the decision, not the code.** The prototype is thrown away; the real build follows the Feature playbook.

1. Name the decision it exists to make: which layout, which interaction, which density, or an observable fork (which approach is faster, does this behaviour feel right). No decision means no prototype.
2. When the direction is open, gather references (what the owner loves and dislikes, from `DESIGN.md` or by asking) and propose variations they didn't ask for.
3. Build in a scratch directory outside the app, with the lightest stack that shows the idea (plain HTML/CSS/JS is fine). No tests, no abstractions.
4. Put the 2-3 variants behind one switcher (buttons or a key), each labelled (Exhaust the design space).
5. Observe: screenshot each variant at 375/768/1280 and drive the interaction; for a behaviour fork, log the timing or output. The observation is the test.
6. Recommend one, with trade-offs, and hand it to the ui-designer (skills `design-critique`, `component-spec`) or the Feature playbook.

**Reply:** the variants, the screenshots or observations, the trade-offs, your recommendation, and the scratch path - stated plainly as throwaway.
