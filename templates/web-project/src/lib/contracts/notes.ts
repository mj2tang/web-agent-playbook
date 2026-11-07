import { z } from "zod";

/** Matches the database constraint on public.notes.body (1-2000 characters). */
export const NOTE_MAX_LENGTH = 2000;

export const NoteInput = z.object({
  body: z
    .string()
    .trim()
    .min(1, "Write something first.")
    .max(NOTE_MAX_LENGTH, `Keep notes under ${NOTE_MAX_LENGTH} characters.`),
});
export type NoteInput = z.infer<typeof NoteInput>;

export const NoteId = z.object({ id: z.uuid() });
