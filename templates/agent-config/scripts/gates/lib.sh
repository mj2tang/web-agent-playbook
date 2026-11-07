# Shared helpers for the gate scripts. Sourced, not run.
# Exit codes: 0 pass, 1 fail, 4 skipped (unless GATES_ALLOW_SKIP=1). A skip is never a pass.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATUS=0
SKIPS=0

pm() {
  if [ -f pnpm-lock.yaml ]; then echo pnpm
  elif [ -f yarn.lock ]; then echo yarn
  elif [ -f bun.lock ] || [ -f bun.lockb ]; then echo bun
  else echo npm; fi
}

# `pm exec`, spelled the way each package manager wants it.
pm_exec() {
  case "$(pm)" in
    npm) npx --no-install "$@" ;;
    yarn) yarn "$@" ;;
    *) "$(pm)" exec "$@" ;;
  esac
}

has_script() {
  [ -f package.json ] && python3 -c 'import json,sys; sys.exit(0 if sys.argv[1] in json.load(open("package.json")).get("scripts", {}) else 1)' "$1"
}

skip() {
  echo "SKIPPED: $1 ($2)"
  SKIPS=$((SKIPS + 1))
}

step() {  # step <name> <command...>
  local name=$1; shift
  echo "▶ $name: $*"
  if "$@"; then echo "PASS: $name"; else echo "FAIL: $name"; STATUS=1; fi
}

finish() {
  if [ "$STATUS" -ne 0 ]; then exit 1; fi
  if [ "$SKIPS" -gt 0 ] && [ "${GATES_ALLOW_SKIP:-0}" != "1" ]; then
    echo "$SKIPS gate step(s) skipped - not a pass. Set GATES_ALLOW_SKIP=1 only if a human accepted the gap."
    exit 4
  fi
  exit 0
}
