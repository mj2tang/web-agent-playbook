import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "{{project}}",
  description: "{{description}}",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-dvh antialiased">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-10 focus:rounded-md focus:bg-surface focus:px-4 focus:py-2"
        >
          Skip to content
        </a>
        <header className="border-b border-border">
          <nav aria-label="Main" className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-4 py-4">
            <Link href="/" className="font-display text-xl">
              {{project}}
            </Link>
            <Link href="/notes" className="rounded-md px-3 py-2 text-sm underline-offset-4 hover:underline">
              Your notes
            </Link>
          </nav>
        </header>
        <main id="main" className="mx-auto max-w-3xl px-4 py-10">
          {children}
        </main>
      </body>
    </html>
  );
}
