"use server";

import { redirect } from "next/navigation";
import { type ActionState, Credentials, fieldErrors } from "@/lib/contracts/auth";
import { createClient } from "@/lib/supabase/server";

type State = ActionState<Credentials>;

export async function authenticate(_prev: State, formData: FormData): Promise<State> {
  const parsed = Credentials.safeParse({ email: formData.get("email"), password: formData.get("password") });
  if (!parsed.success) return { ok: false, fieldErrors: fieldErrors(parsed.error) };

  const supabase = await createClient();
  const intent = formData.get("intent") === "sign-up" ? "sign-up" : "sign-in";
  const { error } =
    intent === "sign-up"
      ? await supabase.auth.signUp(parsed.data)
      : await supabase.auth.signInWithPassword(parsed.data);
  if (error) {
    return {
      ok: false,
      message:
        intent === "sign-up"
          ? "We couldn't create that account. Try another email, or sign in instead."
          : "That email and password don't match. Check them and try again.",
    };
  }
  redirect("/notes");
}

export async function signOut() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/");
}
