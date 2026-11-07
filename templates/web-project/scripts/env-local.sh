#!/usr/bin/env bash
# Write .env.local from the running local Supabase stack (never a hosted project).
set -euo pipefail
cd "$(dirname "$0")/.."
status=$(pnpm exec supabase status -o env 2>/dev/null) || { echo "local Supabase isn't running: make db-start"; exit 1; }
get() { printf '%s\n' "$status" | sed -n "s/^$1=\"\{0,1\}\([^\"]*\)\"\{0,1\}$/\1/p" | head -1; }
url=$(get API_URL)
key=$(get PUBLISHABLE_KEY)
[ -n "$key" ] || key=$(get ANON_KEY)
[ -n "$url" ] && [ -n "$key" ] || { echo "couldn't read API_URL and a publishable/anon key from supabase status"; exit 1; }
case "$url" in http://127.0.0.1:*|http://localhost:*) ;; *) echo "refusing non-local Supabase URL: $url"; exit 1 ;; esac
printf 'NEXT_PUBLIC_SUPABASE_URL=%s\nNEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=%s\n' "$url" "$key" > .env.local
echo "wrote .env.local for $url"
