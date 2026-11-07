#!/usr/bin/env python3
"""Set up web projects for a team of coding agents (Codex + Claude Code).

  playbook.py new  <dir> --name my-site [--description "..."] [--mode vendor|plugin] [--bootstrap]
  playbook.py init <dir> [--profile auto|core|supabase|ui|full] [--guardrails] [--no-link] [--mode vendor|plugin]
  playbook.py sync <dir> [--force]                    # update vendored skills/agents/hooks/scripts

Standard library only. Never overwrites a file the project changed unless --force is given.
`init` never edits package.json, a Makefile, or source; the only edits to existing files are a merge
into .claude/settings.json and one pointer line appended to AGENTS.md (skip it with --no-link).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]
MARKETPLACE = "mj2tang"
PLUGIN = "web-playbook"
PLUGIN_REPO = "mj2tang/web-agent-playbook"
LOCK = ".agents/web-playbook.lock.json"
ML_PLAYBOOK_LOCK = ".agents/playbook.lock.json"
INSTRUCTIONS = "AGENTS.web-playbook.md"
POINTER = "See AGENTS.web-playbook.md for the web agent team's rules, gates, and approvals; read it before any task."
SUPABASE_SKILLS = {"supabase-migrations", "rls-policies", "supabase-auth", "edge-functions-vs-rpc"}
PLAYWRIGHT_CONFIGS = ("playwright.config.ts", "playwright.config.js", "playwright.config.mjs")
UI_DEV_DEPS = ("@playwright/test", "@axe-core/playwright")

# Permission tiers. Existing repos get CORE (the playbook's own scripts and gates) unless they opt in.
PERMISSIONS_CORE = {"allow": [
    "Bash(scripts/agent-team/run-wave.sh:*)", "Bash(python3 scripts/agent-team/audit.py:*)",
    "Bash(python3 scripts/agent-team/panel_review.py:*)",
    "Bash(scripts/gates/check.sh)", "Bash(scripts/gates/db-check.sh)", "Bash(scripts/gates/ui-check.sh)",
]}
PERMISSIONS_WEB = {"allow": [
    "Bash(make check)", "Bash(make db-check)", "Bash(make ui-check)", "Bash(make perf)",
    "Bash(pnpm install --frozen-lockfile)", "Bash(pnpm run:*)", "Bash(pnpm exec vitest:*)",
    "Bash(pnpm exec playwright test:*)", "Bash(pnpm exec tsc:*)", "Bash(pnpm exec eslint:*)",
    "Bash(pnpm exec supabase start)", "Bash(pnpm exec supabase stop)", "Bash(pnpm exec supabase status)",
    "Bash(pnpm exec supabase db reset)", "Bash(pnpm exec supabase test db)",
    "Bash(pnpm exec supabase migration new:*)", "Bash(pnpm exec supabase gen types typescript --local:*)",
    "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git show:*)",
    "Bash(git add:*)", "Bash(git commit:*)", "Bash(git switch:*)", "Bash(git checkout:*)",
    "Bash(git branch:*)", "Bash(git worktree:*)", "Bash(git merge:*)", "Bash(git revert:*)",
]}
# Only with the guard hook installed: it blocks `git -C x push` / reset / clean and remote Supabase,
# which makes these broad -C rules safe.
PERMISSIONS_GUARDED = {
    "allow": ["Bash(git -C:*)", "Bash(make -C:*)"],
    "ask": ["Bash(git push:*)", "Bash(pnpm add:*)", "Bash(npm install:*)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Edit(./configs/gates.json)"],
}


def hooks_config(guard: str) -> dict:
    def cmd(mode: str) -> list:
        return [{"type": "command", "command": f"python3 {guard} {mode}"}]

    return {
        "PreToolUse": [
            {"matcher": "Bash", "hooks": cmd("bash")},
            {"matcher": "Edit|Write|MultiEdit|NotebookEdit", "hooks": cmd("files")},
        ],
        "PostToolUse": [{"matcher": "Edit|Write|MultiEdit", "hooks": cmd("format")}],
    }


class Scaffolder:
    def __init__(self, target: Path, subs: dict[str, str], force: bool, dry_run: bool):
        self.target = target
        self.subs = subs
        self.force = force
        self.dry_run = dry_run
        self.lock: dict[str, str] = {}
        self.report: dict[str, list[str]] = {"created": [], "updated": [], "skipped": []}
        self.notes: list[str] = []
        lock_path = target / LOCK
        self.old_lock = json.loads(lock_path.read_text())["files"] if lock_path.exists() else {}

    def render(self, text: str) -> str:
        return re.sub(r"\{\{(\w+)\}\}", lambda m: self.subs.get(m.group(1), m.group(0)), text)

    def write(self, rel: str, content: str, managed: bool = False, mode: int | None = None) -> None:
        """Write a file. Managed files are tracked in the lock so `sync` can update them safely."""
        dest = self.target / rel
        digest = hashlib.sha256(content.encode()).hexdigest()
        if dest.exists():
            current = hashlib.sha256(dest.read_bytes()).hexdigest()
            if current == digest:
                if managed:
                    self.lock[rel] = digest
                return
            untouched = managed and self.old_lock.get(rel) == current
            created_this_run = rel in self.report["created"]
            if not (self.force or untouched or created_this_run):
                self.report["skipped"].append(rel)
                if managed and rel in self.old_lock:
                    self.lock[rel] = self.old_lock[rel]
                return
            if not created_this_run:
                self.report["updated"].append(rel)
        else:
            self.report["created"].append(rel)
        if managed:
            self.lock[rel] = digest
        if self.dry_run:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
        if mode:
            dest.chmod(mode)

    def copy_tree(self, src: Path, dest_rel: str, managed: bool = False, exclude: tuple[str, ...] = ()) -> None:
        for path in sorted(src.rglob("*")):
            rel_parts = path.relative_to(src).parts
            if path.is_dir() or path.name == ".DS_Store" or "__pycache__" in path.parts or \
                    "node_modules" in path.parts or (rel_parts and rel_parts[0] in exclude):
                continue
            rel = path.relative_to(src).as_posix()
            mode = 0o755 if os.access(path, os.X_OK) else None
            self.write(f"{dest_rel}/{rel}".lstrip("/"), self.render(path.read_text()), managed=managed, mode=mode)

    def write_or_sidecar(self, rel: str, sidecar_rel: str, content: str) -> bool:
        """Create ``rel`` if absent; otherwise leave it alone and write ``sidecar_rel``. True if sidecar."""
        if (self.target / rel).exists() and rel not in self.old_lock:
            self.write(sidecar_rel, content, managed=True)
            return True
        self.write(rel, content, managed=True)
        return False

    def merge_settings(self, extra: dict, permissions: tuple[dict, ...] = ()) -> None:
        """Merge playbook settings into .claude/settings.json, keeping the project's own entries."""
        path = self.target / ".claude" / "settings.json"
        settings = json.loads(path.read_text()) if path.exists() else {}
        for tier in permissions:
            perms = settings.setdefault("permissions", {})
            for key, rules in tier.items():
                existing = perms.setdefault(key, [])
                existing.extend(r for r in rules if r not in existing)
        for key, value in extra.items():
            if key == "hooks":
                hooks = settings.setdefault("hooks", {})
                for event, entries in value.items():
                    current = hooks.setdefault(event, [])
                    current.extend(e for e in entries if e not in current)
            elif isinstance(value, dict):
                settings.setdefault(key, {}).update(value)
            else:
                settings.setdefault(key, value)
        content = json.dumps(settings, indent=2) + "\n"
        rel = ".claude/settings.json"
        if path.exists() and path.read_text() == content:
            return
        self.report["updated" if path.exists() else "created"].append(rel)
        if not self.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

    def append_line(self, rel: str, line: str) -> None:
        """Append ``line`` once (creating the file if absent), keeping the file's line endings byte for byte."""
        path = self.target / rel
        data = path.read_bytes() if path.exists() else b""
        text = data.decode()
        if line in text.splitlines():
            return
        eol = "\r\n" if "\r\n" in text else "\n"
        self.report["updated" if path.exists() else "created"].append(rel)
        if self.dry_run:
            return
        if not text:
            new = f"{line}{eol}"
        else:
            sep = "" if text.endswith(("\n", "\r\n")) else eol
            new = f"{text}{sep}{eol}{line}{eol}"
        path.write_bytes(new.encode())

    def symlink(self, rel: str, to: str) -> None:
        link = self.target / rel
        if link.is_symlink() or link.exists():
            return
        self.report["created"].append(f"{rel} -> {to}")
        if not self.dry_run:
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(to)

    def save_lock(self) -> None:
        if self.dry_run:
            return
        lock = {"playbook_version": VERSION, "source": PLUGIN_REPO, "files": dict(sorted(self.lock.items()))}
        path = self.target / LOCK
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(lock, indent=2) + "\n")


def resolve_profiles(target: Path, profile: str) -> set[str]:
    if profile == "full":
        return {"supabase", "ui"}
    if profile in ("supabase", "ui"):
        return {profile}
    if profile == "core":
        return set()
    found = set()  # auto
    if (target / "supabase").is_dir():
        found.add("supabase")
    if any((target / c).exists() for c in PLAYWRIGHT_CONFIGS):
        found.add("ui")
    return found


def skills_exclude(profiles: set[str]) -> tuple[str, ...]:
    return () if "supabase" in profiles else tuple(sorted(SUPABASE_SKILLS))


def package_manager(target: Path) -> str:
    for lock, pm in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lock", "bun"), ("bun.lockb", "bun")):
        if (target / lock).exists():
            return pm
    return "npm"


def install_agent_setup(s: Scaffolder, mode: str, *, profiles: set[str], guardrails: bool,
                        existing_repo: bool, link: bool = True) -> None:
    """Skills, subagents, task board, team + gate scripts, Codex config, settings; hooks by option."""
    exclude = skills_exclude(profiles)
    # Skills: Codex reads .agents/skills; Claude Code reads .claude/skills.
    s.copy_tree(ROOT / "skills", ".agents/skills", managed=True, exclude=exclude)
    tiers: list[dict] = [PERMISSIONS_CORE] if existing_repo else [PERMISSIONS_CORE, PERMISSIONS_WEB]
    extra: dict = {}
    if mode == "vendor":
        claude_skills = s.target / ".claude/skills"
        if claude_skills.is_dir() and not claude_skills.is_symlink():
            # The project already keeps its own Claude skills here: add ours alongside, don't replace.
            s.copy_tree(ROOT / "skills", ".claude/skills", managed=True, exclude=exclude)
        else:
            s.symlink(".claude/skills", "../.agents/skills")
        s.copy_tree(ROOT / "agents", ".claude/agents", managed=True)
        if guardrails:
            s.write(".claude/hooks/guard.py", (ROOT / "hooks/scripts/guard.py").read_text(), managed=True,
                    mode=0o755)
            extra["hooks"] = hooks_config('"$CLAUDE_PROJECT_DIR"/.claude/hooks/guard.py')
            tiers.append(PERMISSIONS_GUARDED)
    else:
        extra.update({
            "extraKnownMarketplaces": {MARKETPLACE: {"source": {"source": "github", "repo": PLUGIN_REPO}}},
            "enabledPlugins": {f"{PLUGIN}@{MARKETPLACE}": True},
        })
    s.merge_settings(extra, tuple(tiers))
    cfg = ROOT / "templates/agent-config"
    s.copy_tree(cfg / "tasks", "tasks")
    s.copy_tree(cfg / "docs", "docs")  # pipeline map: project-owned
    s.copy_tree(cfg / "configs", "configs")
    s.copy_tree(cfg / "scripts", "scripts", managed=True)
    codex = s.render((cfg / ".codex/config.toml").read_text())
    if s.write_or_sidecar(".codex/config.toml", ".codex/web-playbook.config.toml", codex):
        s.notes.append("codex: your .codex/config.toml was not touched. Copy the [mcp_servers.*] tables you want "
                       "from .codex/web-playbook.config.toml:\n" +
                       "".join(f"    {line}\n" for line in codex.splitlines() if line.startswith("[mcp_servers")))
    if "supabase" in profiles:
        s.copy_tree(ROOT / "templates/profiles/supabase", "")
    if existing_repo and "ui" in profiles:
        s.copy_tree(ROOT / "templates/profiles/ui", "")
        pkg = s.target / "package.json"
        deps = json.loads(pkg.read_text()) if pkg.exists() else {}
        have = {**deps.get("dependencies", {}), **deps.get("devDependencies", {})}
        missing = [d for d in UI_DEV_DEPS if d not in have]
        if missing:
            pm = package_manager(s.target)
            add = {"npm": "npm install -D", "yarn": "yarn add -D", "bun": "bun add -d"}.get(pm, f"{pm} add -D")
            s.notes.append(f"ui: package.json was not changed. To run the playbook's a11y checks, run:\n"
                           f"    {add} {' '.join(missing)}\n    {'npx' if pm == 'npm' else pm + ' exec'} "
                           "playwright install chromium")
    agents_md = s.render((cfg / "AGENTS.md").read_text())
    if existing_repo:
        s.write(INSTRUCTIONS, agents_md, managed=True)
        if link:
            s.append_line("AGENTS.md", POINTER)
        if not (s.target / "CLAUDE.md").exists():
            s.write("CLAUDE.md", f"@{INSTRUCTIONS}\n")
        else:
            claude_md = (s.target / "CLAUDE.md").read_text()
            if f"@{INSTRUCTIONS}" not in claude_md and "@AGENTS.md" not in claude_md:
                s.notes.append(f"claude: your CLAUDE.md was not touched. Add `@{INSTRUCTIONS}` to it so Claude "
                               "Code loads the team rules.")
    else:
        s.write("CLAUDE.md", s.render((cfg / "CLAUDE.md").read_text()))
        # `next dev` upserts this block into AGENTS.md; shipping it verbatim keeps a fresh checkout clean.
        s.write("AGENTS.md", agents_md + "\n" + (ROOT / "templates/nextjs-agent-rules.md").read_text())


def git(target: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(target), *args], check=True, capture_output=True)


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-") or "web-app"


def cmd_new(a: argparse.Namespace) -> int:
    target = Path(a.dir).resolve()
    if target.exists() and any(target.iterdir()) and not a.force:
        print(f"{target} is not empty; use `init` for existing projects (or --force).")
        return 1
    subs = {"project": a.name, "package": slug(a.name), "description": a.description}
    s = Scaffolder(target, subs, a.force, a.dry_run)
    s.copy_tree(ROOT / "templates/web-project", "")
    install_agent_setup(s, a.mode, profiles={"supabase", "ui"}, guardrails=True, existing_repo=False)
    s.save_lock()
    print_report(s, target)
    if a.dry_run:
        return 0
    if not (target / ".git").exists():
        git(target, "init", "-q", "-b", "main")
        git(target, "add", "-A")
        try:
            git(target, "commit", "-q", "-m", f"Scaffold {a.name} with web-agent-playbook {VERSION}")
            print("git: initialised repo on main with an initial commit")
        except subprocess.CalledProcessError:
            # Usually no git identity configured; worktrees need a commit, so tell the user.
            print("git: initialised repo, but the initial commit failed (is user.name/user.email set?). "
                  "Commit manually before running the agent team.")
            return 0 if not a.bootstrap else 1
    if a.bootstrap:
        print("bootstrap: pnpm install, make check ...")
        for step in (["pnpm", "install"], ["make", "check"]):
            subprocess.run(step, cwd=target, check=True)
        # The lockfile too: worktrees are checked out from git, so an uncommitted lock leaves workers unpinned.
        git(target, "add", "pnpm-lock.yaml")
        git(target, "commit", "-q", "-m", "Lock dependencies")
    else:
        print("next: cd into the project, run `pnpm install && make check`, commit pnpm-lock.yaml, then "
              "`pnpm exec supabase start && make db-check`")
    return 0


def cmd_init(a: argparse.Namespace) -> int:
    target = Path(a.dir).resolve()
    if not target.is_dir():
        print(f"{target} does not exist")
        return 1
    if (target / ML_PLAYBOOK_LOCK).exists():
        print(f"{target} already has coding-agent-playbook installed ({ML_PLAYBOOK_LOCK}). Installing both into one "
              "repo isn't supported yet: they share agent and skill names.")
        return 1
    name = a.name or target.name
    s = Scaffolder(target, {"project": name, "package": slug(name), "description": a.description}, a.force, a.dry_run)
    profiles = resolve_profiles(target, a.profile)
    install_agent_setup(s, a.mode, profiles=profiles, guardrails=a.guardrails, existing_repo=True,
                        link=not a.no_link)
    s.save_lock()
    print_report(s, target)
    print(f"profiles: {', '.join(sorted(profiles)) or 'core'}")
    for note in s.notes:
        print(f"note: {note}")
    if a.no_link:
        print(f"note: AGENTS.md was not touched (--no-link). Codex reads only AGENTS.md, so add a pointer to "
              f"{INSTRUCTIONS} yourself or Codex won't see the team rules.")
    if not a.guardrails:
        print("note: guard hooks not installed (no change to what your sessions may run). Add --guardrails to "
              "block pushes, deploys, and remote Supabase and to ask before new dependencies.")
    return 0


def cmd_sync(a: argparse.Namespace) -> int:
    target = Path(a.dir).resolve()
    lock_path = target / LOCK
    if not lock_path.exists():
        print("no web-playbook lock found; run `init` first")
        return 1
    old = json.loads(lock_path.read_text())["files"]
    profiles = {"supabase"} if any(f".agents/skills/{n}/" in k for k in old for n in SUPABASE_SKILLS) else set()
    exclude = skills_exclude(profiles)
    mode = "vendor" if (target / ".claude/agents/orchestrator.md").exists() else "plugin"
    s = Scaffolder(target, {}, a.force, a.dry_run)
    s.copy_tree(ROOT / "skills", ".agents/skills", managed=True, exclude=exclude)
    if mode == "vendor":
        s.copy_tree(ROOT / "agents", ".claude/agents", managed=True)
        claude_skills = target / ".claude/skills"
        if claude_skills.is_dir() and not claude_skills.is_symlink():
            s.copy_tree(ROOT / "skills", ".claude/skills", managed=True, exclude=exclude)
        if (target / ".claude/hooks/guard.py").exists():  # only if guardrails were installed
            s.write(".claude/hooks/guard.py", (ROOT / "hooks/scripts/guard.py").read_text(), managed=True,
                    mode=0o755)
    s.copy_tree(ROOT / "templates/agent-config/scripts", "scripts", managed=True)
    # Keep the rest of the lock (instructions, codex config) so later syncs still know they're untouched.
    for rel, digest in old.items():
        s.lock.setdefault(rel, digest)
    s.save_lock()
    print_report(s, target)
    if s.report["skipped"]:
        print("skipped files were edited locally; re-run with --force to overwrite them")
    return 0


def print_report(s: Scaffolder, target: Path) -> None:
    prefix = "[dry-run] " if s.dry_run else ""
    print(f"{prefix}{target}: {len(s.report['created'])} created, "
          f"{len(s.report['updated'])} updated, {len(s.report['skipped'])} skipped")
    for rel in s.report["skipped"]:
        print(f"  skipped (exists/modified): {rel}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("new", "init", "sync"):
        sp = sub.add_parser(name)
        sp.add_argument("dir")
        sp.add_argument("--force", action="store_true")
        sp.add_argument("--dry-run", action="store_true")
        if name != "sync":
            sp.add_argument("--name", required=name == "new")
            sp.add_argument("--description", default="A website built by a team of coding agents.")
            sp.add_argument("--mode", choices=["vendor", "plugin"], default="vendor",
                            help="vendor: copy skills/agents/hooks into the repo (default). "
                                 "plugin: enable the web-playbook Claude Code plugin instead.")
        if name == "init":
            sp.add_argument("--profile", choices=["auto", "core", "supabase", "ui", "full"], default="auto",
                            help="auto (default): supabase if supabase/ exists, ui if a Playwright config exists. "
                                 "supabase: Supabase skills + RLS-on-every-table test. ui: standalone Playwright "
                                 "config + axe spec (prints the dev-dependency command; never installs)")
            sp.add_argument("--guardrails", action="store_true",
                            help="also install the guard hook (blocks push/deploy/remote Supabase, asks before "
                                 "new dependencies and snapshot updates)")
            sp.add_argument("--no-link", action="store_true",
                            help=f"don't append the one-line pointer to {INSTRUCTIONS} in AGENTS.md")
        if name == "new":
            sp.add_argument("--bootstrap", action="store_true",
                            help="also run pnpm install and make check, and commit the lockfile")
    a = p.parse_args()
    return {"new": cmd_new, "init": cmd_init, "sync": cmd_sync}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
