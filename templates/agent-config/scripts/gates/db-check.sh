#!/usr/bin/env bash
# Gate: migrations apply from zero, pgTAP tests (incl. RLS on every table), generated types up to date.
# Local Supabase only (needs Docker: `supabase start`). Never --linked or --db-url.
source "$(dirname "$0")/lib.sh"

if [ ! -d supabase ]; then skip db-check "no supabase/ directory"; finish; fi
step "db reset" pm_exec supabase db reset
if [ -d supabase/tests ]; then step "pgTAP" pm_exec supabase test db; else skip pgTAP "no supabase/tests/"; fi
if has_script db:types:check; then step "types up to date" "$(pm)" run db:types:check
else skip "types up to date" 'no "db:types:check" script in package.json'; fi
finish
