#!/usr/bin/env python3
"""Install the web-agent-playbook into COPIES of existing projects and prove it does no harm.

  python3 scripts/check_install_safety.py <playbook-dir> <scratch-dir> <project> [<project> ...]

Your projects are only read (copied, excluding node_modules/build output); all installs happen in the copies.

For each (project, mode): copy the project (originals are never touched), fingerprint every file
and the git state, install, fingerprint again, and check:
  - no file deleted; no pre-existing file modified except .claude/settings.json and AGENTS.md
  - .claude/settings.json (if it existed) is a strict superset of the original
  - AGENTS.md (if it existed) is the original bytes plus exactly the one pointer line - nothing else
  - every new path is inside the playbook's footprint
  - git HEAD, branch, stash and the content of pre-existing uncommitted changes are unchanged
  - a second install is a no-op (idempotent)
Modes: vendor (init), plugin (init --mode plugin), full (init --profile full --guardrails),
no-link (init --no-link: AGENTS.md must be untouched). SAFETY_CLI=1 adds cli (claude plugin install).
Exits 1 if any check fails.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PLAYBOOK = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
PROJECTS = [Path(p).resolve() for p in sys.argv[3:]]
EXCLUDE = {"node_modules", ".next", ".turbo", "dist", "build", "coverage", ".venv", "__pycache__",
           "playwright-report", "test-results"}
FOOTPRINT = (".agents/", ".claude/agents/", ".claude/skills", ".claude/hooks/", "tasks/", "scripts/agent-team/",
             "scripts/gates/", "docs/pipeline-map/", "configs/team.json", "configs/gates.json", "AGENTS.web-playbook.md",
             ".claude/settings.json", ".codex/config.toml", ".codex/web-playbook.config.toml", ".codex/agents/",
             "supabase/tests/rls_enabled.test.sql", "playwright.playbook.config.ts", "tests/e2e-playbook/",
             "CLAUDE.md", "AGENTS.md")
CREATE_ONLY = ("CLAUDE.md", ".codex/config.toml")  # may be created, never modified
POINTER = "See AGENTS.web-playbook.md for the web agent team's rules, gates, and approvals; read it before any task."
# Allowed edits, verified by content above; excluded from the git-state comparison.
CHECKED_SEPARATELY = ("AGENTS.md", ".claude/settings.json")
MODES = ["vendor", "plugin", "full", "no-link"] + (["cli"] if os.environ.get("SAFETY_CLI") == "1" else [])


def fingerprint(root: Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if rel.startswith(".git/") or rel == ".git" or set(p.relative_to(root).parts) & EXCLUDE:
            continue
        if p.is_symlink():
            out[rel] = "symlink:" + str(p.readlink())
        elif p.is_file():
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def git_state(root: Path) -> dict[str, str]:
    if not (root / ".git").exists():
        return {}

    def g(*a: str) -> str:
        return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True).stdout.strip()

    return {"head": g("rev-parse", "HEAD"), "branch": g("branch", "--show-current"), "stash": g("stash", "list"),
            "dirty_tracked": "\n".join(f for f in g("diff", "--name-only").splitlines() if f not in CHECKED_SEPARATELY),
            "dirty_diff": g("diff", "--", ".", *(f":(exclude){f}" for f in CHECKED_SEPARATELY))}


def superset(old: object, new: object, path: str = "") -> list[str]:
    """Problems where `new` drops or changes something from `old` (lists may grow, dicts may gain keys)."""
    if isinstance(old, dict) and isinstance(new, dict):
        probs = []
        for k, v in old.items():
            if k not in new:
                probs.append(f"{path}/{k} removed")
            else:
                probs += superset(v, new[k], f"{path}/{k}")
        return probs
    if isinstance(old, list) and isinstance(new, list):
        return [f"{path}: item {x!r} removed" for x in old if x not in new]
    return [] if old == new else [f"{path}: {old!r} -> {new!r}"]


def pointer_only(old: bytes, new: bytes) -> bool:
    """True if `new` is `old` plus exactly one appended pointer line (same line endings)."""
    text = old.decode()
    eol = "\r\n" if "\r\n" in text else "\n"
    sep = "" if not text or text.endswith(("\n", "\r\n")) else eol
    expected = f"{POINTER}{eol}" if not text else f"{text}{sep}{eol}{POINTER}{eol}"
    return new.decode() == expected


def install(proj: Path, mode: str) -> str:
    base = [sys.executable, str(PLAYBOOK / "scripts/playbook.py"), "init", str(proj)]
    extra = {"vendor": [], "plugin": ["--mode", "plugin"], "full": ["--profile", "full", "--guardrails"],
             "no-link": ["--no-link"]}
    if mode == "cli":
        out = []
        for c in (["claude", "plugin", "marketplace", "add", str(PLAYBOOK), "--scope", "project"],
                  ["claude", "plugin", "install", "web-playbook@mj2tang", "--scope", "project", "-y"]):
            r = subprocess.run(c, cwd=proj, capture_output=True, text=True, timeout=300)
            out.append(f"$ {' '.join(c[:4])} ... -> {r.returncode}\n{r.stdout[-400:]}{r.stderr[-400:]}")
        return "\n".join(out)
    r = subprocess.run(base + extra[mode], capture_output=True, text=True)
    return r.stdout + r.stderr + ("" if r.returncode == 0 else f"\n(exit {r.returncode})")


def check(src: Path, mode: str) -> dict[str, object]:
    proj = OUT / f"{src.name}-{mode}"
    if proj.exists():
        shutil.rmtree(proj)
    shutil.copytree(src, proj, symlinks=True, ignore=shutil.ignore_patterns(*EXCLUDE))
    before, git_before = fingerprint(proj), git_state(proj)
    agents_before = (proj / "AGENTS.md").read_bytes() if (proj / "AGENTS.md").exists() else None
    settings_before = json.loads((proj / ".claude/settings.json").read_text()) \
        if (proj / ".claude/settings.json").exists() else None
    log = install(proj, mode)
    after, git_after = fingerprint(proj), git_state(proj)

    added = sorted(set(after) - set(before))
    deleted = sorted(set(before) - set(after))
    modified = sorted(k for k in set(before) & set(after) if before[k] != after[k])
    problems = [f"deleted: {p}" for p in deleted]
    if "(exit " in log:
        problems.append(f"install failed: {log[-300:]}")
    for p in modified:
        if p == ".claude/settings.json":
            continue
        if p == "AGENTS.md" and mode not in ("no-link", "cli") and pointer_only(agents_before, (proj / p).read_bytes()):
            continue
        problems.append(f"modified pre-existing file: {p}")
    if "AGENTS.md" in added and mode not in ("no-link", "cli") and not pointer_only(b"", (proj / "AGENTS.md").read_bytes()):
        problems.append("created AGENTS.md with more than the pointer line")
    problems += [f"new path outside playbook footprint: {p}" for p in added if not p.startswith(FOOTPRINT)]
    problems += [f"modified create-only file: {p}" for p in modified if p in CREATE_ONLY]
    if settings_before is not None and ".claude/settings.json" in modified:
        problems += [f"settings.json {x}" for x in superset(settings_before, json.loads(
            (proj / ".claude/settings.json").read_text()))]
    if git_before != git_after:
        problems.append(f"git state changed: {git_before} -> {git_after}")

    second = fingerprint(proj)
    settings_after = json.loads((proj / ".claude/settings.json").read_text()) \
        if (proj / ".claude/settings.json").exists() else None
    log2 = install(proj, mode)
    third = fingerprint(proj)
    rerun_changes = sorted(k for k in set(second) | set(third) if second.get(k) != third.get(k))
    if ".claude/settings.json" in rerun_changes and settings_after == json.loads(
            (proj / ".claude/settings.json").read_text()):
        rerun_changes.remove(".claude/settings.json")  # re-serialisation is fine if the content is the same
    if rerun_changes:
        problems.append(f"second install changed: {rerun_changes[:5]}")
    return {"project": src.name, "mode": mode, "copy": str(proj), "added": len(added),
            "added_top": sorted({a.split('/')[0] + ('/' if '/' in a else '') for a in added}),
            "modified": modified, "deleted": deleted, "problems": problems, "install_log": log[-1500:],
            "rerun_log": log2[-300:]}


OUT.mkdir(parents=True, exist_ok=True)
results = [check(p, m) for p in PROJECTS for m in MODES]
(OUT / "results.json").write_text(json.dumps(results, indent=2))
for r in results:
    status = "PASS" if not r["problems"] else "FAIL"
    print(f"{status} {r['project']:14s} {r['mode']:7s} added={r['added']:3d} modified={r['modified']} "
          f"deleted={len(r['deleted'])} top={r['added_top']}")
    for p in r["problems"]:
        print(f"    - {p}")
sys.exit(1 if any(r["problems"] for r in results) else 0)
