"use client";

import { useActionState } from "react";
import { authenticate } from "./actions";

export function LoginForm() {
  const [state, action, pending] = useActionState(authenticate, { ok: false });
  const errors = state.fieldErrors ?? {};

  return (
    <form action={action} className="space-y-5" noValidate>
      {state.message ? (
        <p role="alert" className="rounded-md border border-danger px-4 py-3 text-danger">
          {state.message}
        </p>
      ) : null}
      <div className="space-y-2">
        <label htmlFor="email" className="block font-medium">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          aria-invalid={errors.email ? true : undefined}
          aria-describedby={errors.email ? "email-error" : undefined}
          className="w-full rounded-md border border-border bg-surface px-3 py-2"
        />
        {errors.email ? (
          <p id="email-error" className="text-sm text-danger">
            {errors.email}
          </p>
        ) : null}
      </div>
      <div className="space-y-2">
        <label htmlFor="password" className="block font-medium">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          aria-invalid={errors.password ? true : undefined}
          aria-describedby={errors.password ? "password-error" : "password-hint"}
          className="w-full rounded-md border border-border bg-surface px-3 py-2"
        />
        <p id="password-hint" className="text-sm text-muted">
          At least 8 characters.
        </p>
        {errors.password ? (
          <p id="password-error" className="text-sm text-danger">
            {errors.password}
          </p>
        ) : null}
      </div>
      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          name="intent"
          value="sign-in"
          disabled={pending}
          className="rounded-md bg-accent px-5 py-2 font-medium text-accent-fg disabled:opacity-60"
        >
          Sign in
        </button>
        <button
          type="submit"
          name="intent"
          value="sign-up"
          disabled={pending}
          className="rounded-md border border-border px-5 py-2 font-medium disabled:opacity-60"
        >
          Create account
        </button>
      </div>
    </form>
  );
}
