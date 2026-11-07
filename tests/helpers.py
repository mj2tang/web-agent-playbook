"""Shared test helpers."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK = [sys.executable, str(ROOT / "scripts" / "playbook.py")]


def frontmatter(path: Path) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S)
    assert m, f"{path} has no frontmatter"
    return dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)


def run_playbook(*args, cwd=None, check=True) -> str:
    p = subprocess.run([*PLAYBOOK, *args], cwd=cwd, capture_output=True, text=True, check=False)
    if check and p.returncode != 0:
        raise AssertionError(f"playbook {args} exited {p.returncode}\n{p.stdout}\n{p.stderr}")
    return p.stdout
