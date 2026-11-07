import Link from "next/link";

export default function Home() {
  return (
    <section aria-labelledby="hero-title" className="space-y-6">
      <h1 id="hero-title" className="font-display text-4xl leading-tight">
        Write it down before it slips away.
      </h1>
      <p className="max-w-prose text-lg text-muted">
        A small notes app: sign in, keep short notes, and only you can read them. It is the starting point for your
        own site, built and checked by a team of coding agents.
      </p>
      <Link
        href="/notes"
        className="inline-block rounded-md bg-accent px-5 py-3 font-medium text-accent-fg shadow-sm transition-colors duration-150 hover:opacity-90"
      >
        Open your notes
      </Link>
    </section>
  );
}
