"use server";

import { revalidatePath } from "next/cache";
import { type ActionState, fieldErrors } from "@/lib/contracts/auth";
import { NoteId, NoteInput } from "@/lib/contracts/notes";
import { createClient } from "@/lib/supabase/server";

type State = ActionState<NoteInput>;

export async function addNote(_prev: State, formData: FormData): Promise<State> {
  const parsed = NoteInput.safeParse({ body: formData.get("body") });
  if (!parsed.success) return { ok: false, fieldErrors: fieldErrors(parsed.error) };

  // Server actions are public endpoints: check the user here, not only in the page.
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { ok: false, message: "Your session ended. Sign in again to save notes." };

  // owner defaults to auth.uid() in the database; RLS rejects any other owner.
  const { error } = await supabase.from("notes").insert({ body: parsed.data.body });
  if (error) return { ok: false, message: "That note didn't save. Try again." };
  revalidatePath("/notes");
  return { ok: true, message: "Note saved." };
}

export async function deleteNote(formData: FormData): Promise<void> {
  const parsed = NoteId.safeParse({ id: formData.get("id") });
  if (!parsed.success) return;
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return;
  // RLS limits this to the user's own notes; the owner filter makes the intent explicit.
  await supabase.from("notes").delete().eq("id", parsed.data.id).eq("owner", user.id);
  revalidatePath("/notes");
}
