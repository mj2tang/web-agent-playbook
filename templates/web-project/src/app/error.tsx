"use client";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <section role="alert" className="space-y-4">
      <h1 className="font-display text-2xl">Something went wrong</h1>
      <p className="text-muted">Try again. If it keeps happening, the error reference is {error.digest ?? "unknown"}.</p>
      <button type="button" onClick={reset} className="rounded-md border border-border px-4 py-2">
        Try again
      </button>
    </section>
  );
}
