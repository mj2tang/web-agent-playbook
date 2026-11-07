#!/usr/bin/env python3
"""Guardrail hooks for coding agents on web projects (Claude Code hook protocol).

Reads the hook event JSON on stdin. Exit 2 + stderr blocks the tool call;
exit 0 allows it. Modes:
  bash     PreToolUse(Bash): block irreversible or remote actions (push, deploy, linked/remote
           Supabase); force a human prompt ("ask") for dependency installs, snapshot updates,
           and migration-history repair. Commands are split on ; && || | and newlines and
           checked one simple command at a time. This is a best-effort text matcher, not a
           sandbox: a determined script can hide a command. Works for Claude Code and Codex hooks
           (Codex sends shell commands as Bash {command} and file edits as apply_patch {command: patch}).
  files    PreToolUse(Edit|Write, Codex apply_patch): block edits to protected paths and the
           service-role key in client code; ask before editing a migration that is already committed
  format   PostToolUse(Edit|Write): best-effort prettier on the edited file
"""
import json
import os
import re
import shlex
import subprocess
import sys

# `git` followed by any global options (-C <path>, -c key=val, --git-dir=...) before the subcommand,
# so `git -C ../wt push` is caught the same as `git push`.
GIT = r"\bgit\b(?:\s+(?:-C\s+\S+|-c\s+\S+|--[\w-]+(?:=\S+)?))*\s+"
LOCAL_HOSTS = ("127.0.0.1", "localhost", "0.0.0.0", "[::1]", "host.docker.internal")
SEGMENT_SPLIT = re.compile(r"\|\||&&|[;|\n]|(?<![<>0-9])&(?![>0-9])")
# Tokens that can come before the real command: `npx -y supabase`, `pnpm exec supabase`, `FOO=1 vercel`.
LAUNCHERS = {"npx", "pnpm", "yarn", "bunx", "bun", "npm", "exec", "dlx", "x", "env", "command", "time", "sudo"}

DANGEROUS_BASH = [
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+(/|~|\$HOME)(\s|$)", "recursive delete of / or home"),
    (GIT + r"push\b", "git push (needs human approval)"),
    (GIT + r"reset\s+--hard\b", "git reset --hard discards work"),
    (GIT + r"clean\s+-[a-zA-Z]*f", "git clean deletes untracked files"),
    (r"\bdrop\s+(table|database|schema)\b", "destructive SQL"),
    (r"\bdisable\s+row\s+level\s+security\b", "disabling RLS"),
]
SNAPSHOTS = r"(__screenshots__|-snapshots)(/|\b)"
SEGMENT_BLOCKS = [
    (r"^(?:\w+=\S*\s+)*(?:rm|mv|unlink|git\s+(?:-C\s+\S+\s+)?(?:rm|mv))\b[^\n]*" + SNAPSHOTS,
     "visual snapshots change only via `make baselines` with human approval"),
]

# Allowed only with a human in the loop. In headless runs an "ask" is a denial, which is what we want.
HUMAN_APPROVAL_SEGMENT = [
    (r"^(?:\w+=\S*\s+)*(?:pnpm|npm|yarn|bun)\s+(?:add|install|i)\b(?:\s+-\S+)*\s+[^-\s]", "adding a dependency"),
    (r"\bplaywright\s+test\b[^\n]*(--update-snapshots|\s-u\b)", "updating visual snapshots"),
    (r"\bUPDATE_BASELINES=", "writing visual baselines"),
    (r"\bmake\b[^\n]*\sbaselines\b", "writing visual baselines"),
]

# Supabase CLI: local commands pass, remote ones are blocked, anything else asks.
SUPABASE_REMOTE_FLAGS = ("--linked", "--db-url", "--project-ref", "--project-id")
SUPABASE_VALUE_FLAGS = {"--workdir", "--profile", "--dns-resolver", "--output", "-o", "--network-id"}
SUPABASE_LOCAL = {"start", "stop", "status", "init", "help", "completion", "services", "test", "gen", "seed",
                  ("db", "reset"), ("db", "lint"), ("db", "diff"), ("db", "start"),
                  ("migration", "new"), ("migration", "list"), ("migration", "up"), ("migration", "down"),
                  ("migration", "fetch"), ("functions", "serve"), ("functions", "new")}
SUPABASE_LOCAL_ONLY_WITH_FLAG = {("db", "push"), ("db", "pull"), ("db", "dump"), "storage", "inspect"}
SUPABASE_REMOTE = {"link", "projects", "orgs", "branches", "secrets", "domains", "vanity-subdomains", "backups",
                   "network-bans", "network-restrictions", "ssl-enforcement", "postgres-config", "snippets",
                   ("config", "push"), ("functions", "deploy"), ("functions", "delete"), ("functions", "download")}

# Deploy CLIs: first argument → allowed (anything else, including no argument, deploys or touches prod).
DEPLOY_SAFE = {"vercel": {"dev", "env", "whoami", "login", "logout", "help", "--version", "-v", "inspect", "logs",
                          "list", "ls", "pull", "link"},
               "netlify": None, "wrangler": None, "fly": None, "flyctl": None, "firebase": None}
DEPLOY_WORDS = {"deploy", "publish"}

PROTECTED_PATHS = [
    (r"(^|/)\.env(\.(?!example$)[\w.]+)?$", "secrets file"),
    (r"\.(pem|key|p12)$", "key material"),
    (r"(^|/)\.git/", "git internals"),
    (r"(^|/)configs/gates\.json$", "quality-gate budgets change only with human approval"),
    (r"(__screenshots__|-snapshots)/", "visual snapshots change only via --update-snapshots with human approval"),
    (r"(^|/)supabase/\.temp/", "Supabase link state"),
]
ASK_PATHS = [
    (r"(^|/)playwright(\.playbook)?\.config\.(ts|js|mjs|cjs)$", "the Playwright config holds gate settings (snapshots, projects)"),
    (r"(^|/)(lighthouserc[\w.]*\.json|scripts/lighthouse-config\.mjs)$", "performance budgets come from configs/gates.json"),
]
CLIENT_FILE = re.compile(r"(^|/)(src/)?(app|components|hooks)/|(^|/)lib/supabase/client\.[jt]sx?$")
SERVICE_ROLE = re.compile(r"SERVICE_ROLE|service_role|SUPABASE_SECRET_KEY|sb_secret_")


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


def segments(cmd):
    return [s.strip() for s in SEGMENT_SPLIT.split(cmd) if s.strip()]


def tokens(segment):
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def command_at(toks, names):
    """Index of the token naming one of ``names`` in command position (after env vars and launchers)."""
    for i, tok in enumerate(toks):
        base = os.path.basename(tok)
        name = base.split("@", 1)[0] if base.startswith(tuple(names)) else base
        if name in names:
            return i
        if "=" in tok and not tok.startswith("-") or tok in LAUNCHERS or tok.startswith("-"):
            continue
        return None
    return None


def supabase_verdict(toks):
    i = command_at(toks, {"supabase"})
    if i is None:
        return None
    args = toks[i + 1:]
    if any(a.split("=", 1)[0] in SUPABASE_REMOTE_FLAGS for a in args):
        return "block", "targeting a linked or remote Supabase project"
    words, j = [], 0
    while j < len(args):
        a = args[j]
        if a.startswith("-"):
            j += 2 if a in SUPABASE_VALUE_FLAGS and "=" not in a else 1
            continue
        words.append(a)
        j += 1
    if not words:
        return None  # --version, --help
    local = "--local" in args
    keys = [tuple(words[:2]), words[0]]
    if any(k in SUPABASE_REMOTE for k in keys):
        return "block", f"`supabase {' '.join(words[:2])}` changes a hosted Supabase project"
    if any(k in SUPABASE_LOCAL_ONLY_WITH_FLAG for k in keys):
        return None if local else ("block", f"`supabase {' '.join(words[:2])}` without --local targets the linked project")
    if any(k in SUPABASE_LOCAL for k in keys):
        return None
    if keys[0] == ("migration", "repair") or keys[0] == ("migration", "squash"):
        return "ask", "rewriting migration history"
    return "ask", f"`supabase {' '.join(words[:2])}` (not on the local-only list)"


def deploy_verdict(toks):
    i = command_at(toks, set(DEPLOY_SAFE))
    if i is None:
        return None
    tool = os.path.basename(toks[i]).split("@", 1)[0]
    rest = [a for a in toks[i + 1:] if not a.startswith("-")] or [""]
    safe = DEPLOY_SAFE[tool]
    if safe is not None:
        first = toks[i + 1] if len(toks) > i + 1 else ""
        if rest[0] in safe or first in safe:
            return None
        return "block", f"`{tool}` without a safe subcommand deploys"
    if rest[0] in DEPLOY_WORDS:
        return "block", "deploying"
    return None


PATCH_FILE = re.compile(r"^\*\*\* (Add|Update|Delete) File: (.+)$|^\*\*\* Move to: (.+)$")


def edited_files(tool_input, cwd):
    """(path, added text, deleting) for each file a tool call writes.

    Claude Code: Edit/Write/MultiEdit/NotebookEdit carry file_path plus content/new_string/edits.
    Codex: apply_patch carries the whole patch in tool_input.command (*** Add/Update/Delete File: ...).
    """
    patch = tool_input.get("command") or ""
    if "*** Begin Patch" in patch:
        files, current = [], None
        for line in patch.splitlines():
            m = PATCH_FILE.match(line)
            if m:
                rel = (m.group(2) or m.group(3)).strip()
                current = [os.path.join(cwd, rel) if not os.path.isabs(rel) else rel, [], m.group(1) == "Delete"]
                files.append(current)
            elif current is not None and line.startswith("+"):
                current[1].append(line[1:])
        return [(path, "\n".join(lines), deleting) for path, lines, deleting in files]
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    parts = [tool_input.get(k) or "" for k in ("content", "new_string", "new_source")]
    parts += [e.get("new_string") or "" for e in tool_input.get("edits") or [] if isinstance(e, dict)]
    return [(path, "\n".join(parts), False)]


def file_verdict(path, text, cwd, deleting=False):
    for pattern, reason in PROTECTED_PATHS:
        if re.search(pattern, path):
            return "block", f"{path}: {reason}"
    try:
        existing = open(path, encoding="utf-8", errors="ignore").read(4096) if os.path.isfile(path) else ""
    except OSError:
        existing = ""
    client = CLIENT_FILE.search(path) or re.search(r"""^\s*['"]use client['"]""", text + "\n" + existing, re.M)
    if client and SERVICE_ROLE.search(text):
        return "block", f"{path}: the service-role/secret key bypasses RLS and must stay in server-only modules (src/lib/server/)"
    for pattern, reason in ASK_PATHS:
        if re.search(pattern, path):
            return "ask", f"editing {os.path.basename(path)}: {reason}"
    if re.search(r"(^|/)supabase/migrations/[^/]+\.sql$", path) and committed(path, cwd):
        return "ask", f"{'deleting' if deleting else 'editing'} an applied migration ({os.path.basename(path)}); write a new migration instead"
    return None


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
        asks = []
        for seg in segments(cmd):
            for pattern, reason in SEGMENT_BLOCKS:
                if re.search(pattern, seg):
                    block(reason)
            toks = tokens(seg)
            for verdict in (supabase_verdict(toks), deploy_verdict(toks)):
                if verdict and verdict[0] == "block":
                    block(verdict[1])
                if verdict:
                    asks.append(verdict[1])
            asks += [reason for pattern, reason in HUMAN_APPROVAL_SEGMENT if re.search(pattern, seg)]
        if asks:
            ask(asks[0])
    elif mode == "files":
        asks = []
        for path, text, deleting in edited_files(tool_input, cwd):
            verdict = file_verdict(path, text, cwd, deleting)
            if verdict and verdict[0] == "block":
                block(verdict[1])
            if verdict:
                asks.append(verdict[1])
        if asks:
            ask(asks[0])
    elif mode == "format":
        path = tool_input.get("file_path", "")
        prettier = os.path.join(cwd, "node_modules", ".bin", "prettier")
        if path and os.path.isfile(path) and os.access(prettier, os.X_OK) and \
                re.search(r"\.(ts|tsx|js|jsx|mjs|json|css|md)$", path):
            subprocess.run([prettier, "--write", "--log-level", "warn", path], check=False, timeout=30)
    sys.exit(0)


if __name__ == "__main__":
    main()
