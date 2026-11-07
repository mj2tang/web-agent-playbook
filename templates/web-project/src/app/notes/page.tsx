import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { signOut } from "../login/actions";
import { deleteNote } from "./actions";
import { NoteForm } from "./note-form";

export const metadata: Metadata = { title: "Your notes" };

export default async function NotesPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: notes, error } = await supabase
    .from("notes")
    .select("id, body, created_at")
    .order("created_at", { ascending: false });

  return (
    <section aria-labelledby="notes-title" className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 id="notes-title" className="font-display text-3xl">
          Your notes
        </h1>
        <form action={signOut}>
          <button type="submit" className="rounded-md border border-border px-4 py-2 text-sm">
            Sign out
          </button>
        </form>
      </div>
      <NoteForm />
      {error ? (
        <p role="alert" className="text-danger">
          Your notes didn&apos;t load. Refresh the page to try again.
        </p>
      ) : notes && notes.length > 0 ? (
        <ul className="space-y-3">
          {notes.map((note) => (
            <li
              key={note.id}
              className="flex items-start justify-between gap-4 rounded-md border border-border bg-surface p-4"
            >
              <p className="whitespace-pre-wrap [overflow-wrap:anywhere]">{note.body}</p>
              <form action={deleteNote}>
                <input type="hidden" name="id" value={note.id} />
                <button
                  type="submit"
                  aria-label={`Delete note: ${note.body.slice(0, 40)}`}
                  className="rounded-md px-2 py-1 text-sm text-muted underline-offset-4 hover:underline"
                >
                  Delete
                </button>
              </form>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-muted">No notes yet. Write your first note above.</p>
      )}
    </section>
  );
}
