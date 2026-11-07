### Investigation

**You own a cited answer, not a change.** Read-only.

1. Restate the question and what a good answer lets the user decide.
2. Map the code path: entry route or action, components, server code, queries, policies. Cite `file:line` for each hop.
3. Check history when "why" matters: `git log -S`, `git blame`, the PR that introduced it, `docs/solutions/`, `docs/design/`.
4. Where the answer depends on runtime behaviour (what renders, which query runs, what RLS returns), run it: Playwright or the browser MCP for the page, `psql` as `authenticated` for the query. Don't infer what you can observe.
5. Separate facts (cited or observed) from inferences and guesses.

**Reply:** the answer first, then the evidence chain with `file:line` and observations, then what's still uncertain and how to settle it.
