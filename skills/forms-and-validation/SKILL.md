---
name: forms-and-validation
description: Build forms with one Zod schema shared by client and server - progressive-enhancement server actions, useActionState for pending and errors, accessible labels and error messages, idempotent submits, and server-side validation that never trusts the client. Use when building or changing any form, server action input, or route handler body. Not for read-only pages or search-as-you-type filters without mutations.
---

# Forms and validation

## Procedure
1. **Schema first** in `src/lib/contracts/<thing>.ts`: `export const NoteInput = z.object({ body: z.string().trim().min(1).max(2000) })` and `export type NoteInput = z.infer<typeof NoteInput>`. Match database constraints exactly (same max length, same nullability).
2. **Server action** (`"use server"`) parses `FormData` with `safeParse`. On failure return `{ ok: false, fieldErrors }`; never throw validation errors to the client. Check the user (`supabase.auth.getUser()`) *inside* the action - actions are public endpoints.
3. **Form component:** `<form action={action}>` works without JS; enhance with `useActionState` for pending state and errors, and `useFormStatus` to disable the submit button while pending.
4. **Accessibility:** visible `<label htmlFor>`; errors rendered next to the field with `id` linked by `aria-describedby`; `aria-invalid`; focus the first invalid field (or an error summary) after a failed submit; announce success via `aria-live`.
5. **Resilience:** idempotent writes (unique constraint or upsert) so double-submits don't duplicate; `revalidatePath` / `redirect` after success.
6. **Tests:** Vitest for the schema (valid, empty, too long, wrong type), Playwright for the form (submit with errors, then success, keyboard-only).

## Done when
The same schema validates on both sides, the form works with JS disabled, and tests cover the invalid and valid paths.
