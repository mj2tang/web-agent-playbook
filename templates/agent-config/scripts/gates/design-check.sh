#!/usr/bin/env bash
# Gate: deterministic design lint (tokens, focus, semantics, generic-AI patterns) on UI code, plus
# Impeccable's anti-pattern detector when the project has it installed (`npx impeccable install`).
source "$(dirname "$0")/lib.sh"

dirs=()
for d in src/app src/components app components; do [ -d "$d" ] && dirs+=("$d"); done
if [ ${#dirs[@]} -eq 0 ]; then skip design-check "no src/app, src/components, app, or components directory"; finish; fi
[ -d src/styles ] && dirs+=(src/styles)
step "design-lint" python3 "$(dirname "$0")/design_lint.py" "${dirs[@]}"
if [ -x node_modules/.bin/impeccable ]; then
  step "impeccable detect" pm_exec impeccable detect "${dirs[@]}"
fi
finish
