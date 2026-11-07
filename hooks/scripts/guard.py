#!/usr/bin/env python3
"""Guardrail hooks for coding agents on web projects (Claude Code hook protocol).

Reads the hook event JSON on stdin. Exit 2 + stderr blocks the tool call;
exit 0 allows it. Modes:
  bash     PreToolUse(Bash): block irreversible or remote actions (push, deploy, linked/remote
           Supabase); force a human prompt ("ask") for dependency installs, snapshot updates,
           and migration-history repair
  files    PreToolUse(Edit|Write): block edits to protected paths and the service-role key in
           client code; ask before editing a migration that is already committed
  format   PostToolUse(Edit|Write): best-effort prettier on the edited file
"""
import json
import os
import re
import subprocess
import sys

# `git` followed by any global options (-C <path>, -c key=val, --git-dir=...) before the subcommand,
# so `git -C ../wt push` is caught the same as `git push`.
GIT = r"\bgit\b(?:\s+(?:-C\s+\S+|-c\s+\S+|--[\w-]+(?:=\S+)?))*\s+"
SUPABASE = r"\bsupabase\s+"  # also matches `pnpm exec supabase`, `npx supabase`
PM_ADD = r"\b(?:pnpm|npm|yarn|bun)\s+(?:add|install|i)\s+(?!-)[^\s-]"  # install <pkg>, not a bare install
LOCAL_HOSTS = ("127.0.0.1", "localhost", "0.0.0.0", "[::1]", "host.docker.internal")

DANGEROUS_BASH = [
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+(/|~|\$HOME)(\s|$)", "recursive delete of / or home"),
    (GIT + r"push\b", "git push (needs human approval)"),
    (GIT + r"reset\s+--hard\b", "git reset --hard discards work"),
    (GIT + r"clean\s+-[a-zA-Z]*f", "git clean deletes untracked files"),
    (SUPABASE + r"link\b", "linking a remote Supabase project"),
    (SUPABASE + r"db\s+push\b(?![^\n]*--local\b)", "pushing migrations to a remote database"),
    (SUPABASE + r"(functions\s+deploy|secrets\s+set|secrets\s+unset)\b", "changing a remote Supabase project"),
    (r"--(db-url|project-ref)\b", "targeting a remote Supabase project"),
    (r"\b(vercel|netlify)\b[^\n]*(--prod\b|\bdeploy\b)", "deploying"),
    (r"\bdrop\s+(table|database|schema)\b", "destructive SQL"),
    (r"\bdisable\s+row\s+level\s+security\b", "disabling RLS"),
]

# Allowed only with a human in the loop. In headless runs an "ask" is a denial, which is what we want.
HUMAN_APPROVAL_BASH = [
    (PM_ADD, "adding a dependency"),
    (r"\bplaywright\s+test\b[^\n]*(--update-snapshots|\s-u\b)", "updating visual snapshots"),
    (SUPABASE + r"migration\s+(repair|squash)\b", "rewriting migration history"),
]

PROTECTED_PATHS = [
    (r"(^|/)\.env(\.(?!example$)[\w.]+)?$", "secrets file"),
    (r"\.(pem|key|p12)$", "key material"),
    (r"(^|/)\.git/", "git internals"),
    (r"(^|/)configs/gates\.json$", "quality-gate budgets change only with human approval"),
    (r"(__screenshots__|-snapshots)/", "visual snapshots change only via --update-snapshots with human approval"),
    (r"(^|/)supabase/\.temp/", "Supabase link state"),
]
CLIENT_FILE = re.compile(r"(^|/)src/(app|components)/")
SERVICE_ROLE = re.compile(r"SERVICE_ROLE|service_role")


def block(reason):
    print(f"Blocked by web-playbook guard: {reason}. Ask the user if this is intended.", file=sys.stderr)
    sys.exit(2)


def ask(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": f"web-playbook guard: {reason} needs human approval",
    }}))
    sys.exit(0)


def remote_postgres(cmd):
    for m in re.finditer(r"postgres(?:ql)?://(?:[^@\s/]*@)?([^:/\s?]+)", cmd):
        if m.group(1) not in LOCAL_HOSTS:
            return True
    return False


def committed(path, cwd):
    try:
        p = subprocess.run(["git", "-C", cwd, "ls-files", "--error-unmatch", path], capture_output=True, timeout=10)
    except Exception:
        return False
    return p.returncode == 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    tool_input = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.getcwd()

    if os.environ.get("PLAYBOOK_GUARD_OFF") == "1":
        sys.exit(0)

    if mode == "bash":
        cmd = tool_input.get("command", "")
        for pattern, reason in DANGEROUS_BASH:
            if re.search(pattern, cmd, re.IGNORECASE):
                block(reason)
        if remote_postgres(cmd):
            block("connecting to a non-local database")
        for pattern, reason in HUMAN_APPROVAL_BASH:
            if re.search(pattern, cmd):
                ask(reason)
    elif mode == "files":
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        for pattern, reason in PROTECTED_PATHS:
            if re.search(pattern, path):
                block(f"{path}: {reason}")
        text = (tool_input.get("content") or "") + (tool_input.get("new_string") or "")
        if CLIENT_FILE.search(path) and SERVICE_ROLE.search(text):
            block(f"{path}: the service-role key bypasses RLS and must stay in server-only modules (src/lib/server/)")
        if re.search(r"(^|/)supabase/migrations/[^/]+\.sql$", path) and committed(path, cwd):
            ask(f"editing an applied migration ({os.path.basename(path)}); write a new migration instead")
    elif mode == "format":
        path = tool_input.get("file_path", "")
        prettier = os.path.join(cwd, "node_modules", ".bin", "prettier")
        if path and os.path.isfile(path) and os.access(prettier, os.X_OK) and \
                re.search(r"\.(ts|tsx|js|jsx|mjs|json|css|md)$", path):
            subprocess.run([prettier, "--write", "--log-level", "warn", path], check=False, timeout=30)
    sys.exit(0)


if __name__ == "__main__":
    main()
