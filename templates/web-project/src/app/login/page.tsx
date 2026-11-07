import type { Metadata } from "next";
import { LoginForm } from "./login-form";

export const metadata: Metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <section aria-labelledby="login-title" className="max-w-sm space-y-6">
      <h1 id="login-title" className="font-display text-3xl">
        Sign in
      </h1>
      <p className="text-muted">New here? Enter an email and password, then choose Create account.</p>
      <LoginForm />
    </section>
  );
}
