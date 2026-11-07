#!/usr/bin/env bash
# Gate: Playwright e2e + axe + screenshots. Prefers the playbook's config when installed alongside yours.
source "$(dirname "$0")/lib.sh"

config=""
for c in playwright.playbook.config.ts playwright.config.ts playwright.config.js playwright.config.mjs; do
  [ -f "$c" ] && { config=$c; break; }
done
if [ -z "$config" ]; then skip ui-check "no Playwright config"; finish; fi
step "playwright" pm_exec playwright test --config "$config"
finish
