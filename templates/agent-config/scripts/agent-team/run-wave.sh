#!/usr/bin/env bash
# Run several board tasks in parallel, headless, one git worktree per task.
#   scripts/agent-team/run-wave.sh T-001 T-002 T-003
# Runner: claude (default) or codex — set RUNNER=... or configs/team.json "headless_runner".
# Each worker follows the worker-protocol skill; review with the supervisor before merging.
set -euo pipefail
# Headless Claude ignores the project's permissions.allow rules until the folder has been trusted:
# run `claude` interactively in this project once and accept the trust dialog before using this script.

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
RUNNER=${RUNNER:-$(python3 -c 'import json;print(json.load(open("configs/team.json")).get("headless_runner","claude"))' 2>/dev/null || echo claude)}
BASE=${BASE:-$(python3 -c 'import json;print(json.load(open("configs/team.json")).get("integration_branch","main"))' 2>/dev/null || echo main)}
WT_DIR=${WT_DIR:-"$ROOT/../$(basename "$ROOT")-worktrees"}
LOG_DIR="$ROOT/.agent-logs"
mkdir -p "$WT_DIR" "$LOG_DIR"

[ $# -gt 0 ] || { echo "usage: $0 T-001 [T-002 ...]"; exit 1; }
# Trust ladder: parallelism is earned from the decision trail (scripts/agent-team/audit.py trust).
ALLOWED=$(python3 "$ROOT/scripts/agent-team/audit.py" trust 2>/dev/null || echo 1)
if [ "$#" -gt "$ALLOWED" ] && [ "${FORCE:-0}" = "1" ]; then
  python3 "$ROOT/scripts/agent-team/audit.py" log dispatch "$*" "run-wave" "forced wave of $# over trust limit $ALLOWED" \
    "FORCE=1 set by the operator" "run-wave.sh" forced || true
fi
if [ "$#" -gt "$ALLOWED" ] && [ "${FORCE:-0}" != "1" ]; then
  echo "Trust ladder allows $ALLOWED parallel worker(s); got $# tasks."
  echo "Run fewer tasks, see 'python3 scripts/agent-team/audit.py trust --explain', or override with FORCE=1."
  exit 1
fi

# Package manager from the lockfile (same rule as scripts/gates/lib.sh).
if [ -f pnpm-lock.yaml ]; then PM=pnpm; elif [ -f yarn.lock ]; then PM=yarn
elif [ -f bun.lock ] || [ -f bun.lockb ]; then PM=bun; else PM=npm; fi
case "$PM" in
  pnpm) INSTALL=(pnpm install --frozen-lockfile) ;;
  yarn) INSTALL=(yarn install --frozen-lockfile) ;;
  bun)  INSTALL=(bun install --frozen-lockfile) ;;
  npm)  INSTALL=(npm ci) ;;
esac

# Headless runs ignore the project's permissions.allow until the folder is trusted interactively.
# ALLOW_FROM_SETTINGS=1 passes that allow list to each claude worker instead - only for repos you trust.
ALLOW_ARGS=()
if [ "${ALLOW_FROM_SETTINGS:-0}" = "1" ] && [ -f "$ROOT/.claude/settings.json" ]; then
  while IFS= read -r rule; do ALLOW_ARGS+=("$rule"); done < <(python3 -c \
    "import json,sys; print('\\n'.join(json.load(open(sys.argv[1])).get('permissions', {}).get('allow', [])))" \
    "$ROOT/.claude/settings.json")
  ALLOW_ARGS=(--allowedTools Read Edit Write Glob Grep "${ALLOW_ARGS[@]}")
fi

# Codex: explicit sandbox flags every time - a project .codex/config.toml can be overridden by the user's
# config. Workers get no network (deps are installed below, before dispatch); gates that need Docker,
# localhost, or browsers run in the supervisor's review with network_access=true.
# Codex's workspace-write sandbox keeps .git read-only (worktrees included), so codex workers can't commit:
# the runner commits each worker's owned files after it exits. CODEX_APPROVE_FOR_ME=1 instead lets Codex
# escalate blocked commands (git commit, ...) through its automatic reviewer - only for repos you trust.
CODEX_ARGS=(--sandbox workspace-write -c sandbox_workspace_write.network_access=false)
[ "${CODEX_APPROVE_FOR_ME:-0}" = "1" ] && CODEX_ARGS=(--approve-for-me)
# The package store lives outside the worktree; without write access installs/execs fail in the sandbox.
if [ "$PM" = pnpm ] && command -v pnpm >/dev/null; then
  store=$(pnpm store path 2>/dev/null || true)
  [ -n "$store" ] && CODEX_ARGS+=(--add-dir "$store")
fi
CODEX_NOTE="Codex sandbox: .git is read-only and there is no network, so don't commit or install packages.
Leave your changes in the working tree; this runner commits your owned files when you exit and the supervisor
runs db-check/ui-check (Docker, browsers) on that commit."
[ "${CODEX_APPROVE_FOR_ME:-0}" = "1" ] && CODEX_NOTE=""

# Commit a codex worker's owned files (task front matter) plus its task file; report anything left outside scope.
commit_owned() {
  local wt=$1 task=$2 id=$3 paths
  paths=$(python3 - "$wt/$task" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
fm = text.split("---", 2)[1] if text.startswith("---") else ""
m = re.search(r"^owned_files:[ \t]*\n((?:[ \t]+-[ \t].*\n?)*)", fm, re.M)
for line in m.group(1).splitlines() if m else []:
    print(line.split("-", 1)[1].split(" #")[0].strip())
PY
)
  while IFS= read -r p; do
    [ -n "$p" ] && git -C "$wt" add -A -- "$p" 2>/dev/null || true
  done <<<"$task"$'\n'"$paths"
  if git -C "$wt" diff --cached --quiet; then
    echo "run-wave: nothing to commit for $id"
  else
    git -C "$wt" commit -q -m "$id: worker changes (committed by run-wave for codex)" && \
      echo "run-wave: committed $(git -C "$wt" rev-parse --short HEAD) for $id"
  fi
  local rest
  rest=$(git -C "$wt" status --porcelain)
  [ -z "$rest" ] || printf 'run-wave: left uncommitted (outside owned_files):\n%s\n' "$rest"
}

# Logs stay local whether or not the repo's .gitignore knows about them.
[ -f "$LOG_DIR/.gitignore" ] || echo '*' >"$LOG_DIR/.gitignore"

GATE_HINT="make check (or scripts/gates/check.sh), plus db-check if the task touches supabase/ and ui-check if it touches pages or components"

pids=()
for id in "$@"; do
  task=$(ls tasks/"$id"-*.md 2>/dev/null | head -1) || true
  [ -n "${task:-}" ] || { echo "no task file for $id"; exit 1; }
  slug=$(basename "$task" .md)
  branch="task/$slug"
  wt="$WT_DIR/$slug"
  if [ ! -d "$wt" ]; then
    git worktree add -q "$wt" -b "$branch" "$BASE" 2>/dev/null || git worktree add -q "$wt" "$branch"
  fi
  # Install the worktree's deps here: sandboxed workers (codex) have no network to do it themselves.
  if [ -f "$wt/package.json" ] && command -v "$PM" >/dev/null; then
    (cd "$wt" && "${INSTALL[@]}" >/dev/null) || echo "warning: $PM install failed in $wt; the worker may not be able to run gates"
  fi
  prompt="You are a worker on this web project's agent team. Follow the worker-protocol skill exactly.
Task file: $task. Branch: $branch (already checked out in this worktree).
Gates: $GATE_HINT.
Do not push. Finish with the worker-protocol summary block."
  echo "▶ $id → $wt ($RUNNER)"
  python3 "$ROOT/scripts/agent-team/audit.py" log dispatch "$id" "run-wave:$RUNNER" "dispatched $branch" "wave of $# (trust limit $ALLOWED$([ "$#" -gt "$ALLOWED" ] && echo ", forced"))" "$wt" started || true
  case "$RUNNER" in
    claude) (cd "$wt" && claude -p "$prompt" --permission-mode acceptEdits ${ALLOW_ARGS[@]+"${ALLOW_ARGS[@]}"} >"$LOG_DIR/$slug.log" 2>&1) & ;;
    codex)  (cd "$wt"; rc=0; codex exec "${CODEX_ARGS[@]}" "$prompt
$CODEX_NOTE" >"$LOG_DIR/$slug.log" 2>&1 || rc=$?
             commit_owned "$wt" "$task" "$id" >>"$LOG_DIR/$slug.log" 2>&1; exit $rc) & ;;
    *) echo "unknown RUNNER=$RUNNER"; exit 1 ;;
  esac
  pids+=($!)
done

fail=0
for pid in "${pids[@]}"; do wait "$pid" || fail=1; done
echo "Wave finished (logs in $LOG_DIR). Next: review each branch with the supervisor, then merge-train."
exit $fail
