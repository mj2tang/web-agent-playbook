import { z } from "zod";

export const Credentials = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(8, "Use at least 8 characters."),
});
export type Credentials = z.infer<typeof Credentials>;

/** Field errors as plain strings, ready for aria-describedby messages. */
export type FieldErrors<T> = Partial<Record<keyof T, string>>;

export type ActionState<T> = { ok: boolean; message?: string; fieldErrors?: FieldErrors<T> };

export function fieldErrors<T>(error: z.ZodError<T>): FieldErrors<T> {
  const out: Record<string, string> = {};
  for (const issue of error.issues) {
    const key = String(issue.path[0] ?? "form");
    out[key] ??= issue.message;
  }
  return out as FieldErrors<T>;
}
