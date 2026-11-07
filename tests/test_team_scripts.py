"""Decision trail + trust ladder (audit.py) and run-wave.sh (trust enforcement, codex commit step)."""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import ROOT  # noqa: E402

TEAM = ROOT / "templates/agent-config/scripts/agent-team"
AUDIT = TEAM / "audit.py"
spec = importlib.util.spec_from_file_location("audit", AUDIT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

SETTINGS = {"start_workers": 1, "max_workers": 3, "promote_after": 2}
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def rows(*results):
    return [{"ts": f"t{i}", "task": f"T-{i}", "result": r} for i, r in enumerate(results)]


def make_project(path: Path) -> None:
    """A committed repo with the team scripts, team config and a pnpm lockfile."""
    (path / "scripts").mkdir(parents=True)
    shutil.copytree(TEAM, path / "scripts/agent-team")
    (path / "configs").mkdir()
    shutil.copy(ROOT / "templates/agent-config/configs/team.json", path / "configs/team.json")
    (path / "tasks").mkdir()
    (path / "package.json").write_text('{"name": "p"}')
    (path / "pnpm-lock.yaml").write_text("")
    (path / "src/app").mkdir(parents=True)
    (path / "src/app/page.tsx").write_text("export default function P() { return null }\n")
    env = {**os.environ, **GIT_ENV}
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "init"]):
        subprocess.run(["git", "-C", str(path), *args], check=True, env=env, capture_output=True)


class TestTrustLadder(unittest.TestCase):
    def test_starts_low_and_is_earned(self):
        self.assertEqual(audit.trust_level([], SETTINGS)[0], 1)
        self.assertEqual(audit.trust_level(rows("approved"), SETTINGS)[0], 1)
        self.assertEqual(audit.trust_level(rows("approved", "approved"), SETTINGS)[0], 2)
        self.assertEqual(audit.trust_level(rows(*["approved"] * 10), SETTINGS)[0], 3)

    def test_failures_demote(self):
        self.assertEqual(audit.trust_level(rows("approved", "approved", "reverted"), SETTINGS)[0], 1)
        self.assertEqual(audit.trust_level(rows("approved", "changes_requested", "approved"), SETTINGS)[0], 1)


class TestRunWave(unittest.TestCase):
    def test_refuses_wave_larger_than_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "p"
            make_project(proj)
            for i in (1, 2):
                (proj / f"tasks/T-00{i}-x.md").write_text("---\nid: T-00%d\n---\n" % i)
            r = subprocess.run(["bash", "scripts/agent-team/run-wave.sh", "T-001", "T-002"], cwd=proj,
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("Trust ladder allows 1", r.stdout)

    def test_codex_runner_installs_deps_and_commits_owned_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "p"
            make_project(proj)
            (proj / "tasks/T-001-x.md").write_text(
                "---\nid: T-001\nowned_files:\n  - src/app/page.tsx\n  - tests/unit/  # new tests\n---\n")
            env = {**os.environ, **GIT_ENV}
            subprocess.run(["git", "-C", str(proj), "add", "-A"], check=True, env=env)
            subprocess.run(["git", "-C", str(proj), "commit", "-qm", "task"], check=True, env=env)
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            (bin_dir / "codex").write_text(
                '#!/bin/sh\nprintf "%s\\n" "$@" > "$ARGS_OUT"\n'
                'echo "// x" >> src/app/page.tsx\nmkdir -p tests/unit\necho "test" > tests/unit/x.test.ts\n'
                'echo stray > README.md\n')
            (bin_dir / "pnpm").write_text('#!/bin/sh\necho "pnpm $*" >> "$PNPM_OUT"\n'
                                          '[ "$1" = "store" ] && echo "$STORE"\nexit 0\n')
            for f in bin_dir.iterdir():
                f.chmod(0o755)
            env.update({"PATH": f"{bin_dir}:{os.environ['PATH']}", "RUNNER": "codex",
                        "ARGS_OUT": str(Path(tmp) / "args"), "PNPM_OUT": str(Path(tmp) / "pnpm"),
                        "STORE": str(Path(tmp) / "store")})
            r = subprocess.run(["bash", "scripts/agent-team/run-wave.sh", "T-001"], cwd=proj, env=env,
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            wt = proj.parent / "p-worktrees/T-001-x"
            committed = subprocess.run(["git", "-C", str(wt), "show", "--name-only", "--format=%s", "HEAD"],
                                       capture_output=True, text=True, check=True).stdout
            self.assertIn("T-001: worker changes", committed)
            self.assertIn("src/app/page.tsx", committed)
            self.assertIn("tests/unit/x.test.ts", committed)
            self.assertNotIn("README.md", committed)
            log = (proj / ".agent-logs/T-001-x.log").read_text()
            self.assertIn("outside owned_files", log)
            args = (Path(tmp) / "args").read_text().splitlines()
            self.assertIn("workspace-write", args)
            self.assertIn("sandbox_workspace_write.network_access=false", args)
            self.assertIn(str(Path(tmp) / "store"), args)  # pnpm store writable for the sandbox
            self.assertIn("install --frozen-lockfile", (Path(tmp) / "pnpm").read_text())
            self.assertEqual((proj / ".agent-logs/.gitignore").read_text().strip(), "*")


if __name__ == "__main__":
    unittest.main()
