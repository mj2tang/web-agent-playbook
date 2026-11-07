#!/usr/bin/env bash
# Gate: lint, typecheck, unit tests - using the repo's own package.json scripts.
source "$(dirname "$0")/lib.sh"

if has_script lint; then step lint "$(pm)" run lint; else skip lint 'no "lint" script in package.json'; fi
if has_script typecheck; then step typecheck "$(pm)" run typecheck
elif [ -f tsconfig.json ]; then step typecheck pm_exec tsc --noEmit
else skip typecheck 'no "typecheck" script or tsconfig.json'; fi
if has_script test; then step test "$(pm)" run test; else skip test 'no "test" script in package.json'; fi
finish
