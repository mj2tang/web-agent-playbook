"use client";

import { useActionState, useEffect, useRef } from "react";
import { NOTE_MAX_LENGTH } from "@/lib/contracts/notes";
import { addNote } from "./actions";

export function NoteForm() {
  const [state, action, pending] = useActionState(addNote, { ok: false });
  const formRef = useRef<HTMLFormElement>(null);
  const error = state.fieldErrors?.body;

  useEffect(() => {
    if (state.ok) formRef.current?.reset();
  }, [state]);

  return (
    <form ref={formRef} action={action} className="space-y-3" noValidate>
      <label htmlFor="body" className="block font-medium">
        New note
      </label>
      <textarea
        id="body"
        name="body"
        rows={3}
        maxLength={NOTE_MAX_LENGTH}
        required
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? "body-error" : undefined}
        className="w-full rounded-md border border-border bg-surface px-3 py-2"
      />
      {error ? (
        <p id="body-error" className="text-sm text-danger">
          {error}
        </p>
      ) : null}
      <div className="flex items-center gap-4">
        <button
          type="submit"
          disabled={pending}
          className="rounded-md bg-accent px-5 py-2 font-medium text-accent-fg disabled:opacity-60"
        >
          {pending ? "Saving…" : "Save note"}
        </button>
        <p aria-live="polite" className={state.ok ? "text-sm text-success" : "text-sm text-danger"}>
          {state.message ?? ""}
        </p>
      </div>
    </form>
  );
}
