"""check_install_safety.py: passes for the real installer, catches an installer that over-edits AGENTS.md."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import ROOT  # noqa: E402

CHECK = ROOT / "scripts/check_install_safety.py"
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def fixture_repo(path: Path) -> None:
    path.mkdir(parents=True)
    (path / "package.json").write_text('{"name": "site", "scripts": {"lint": "eslint ."}}\n')
    (path / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
    (path / "AGENTS.md").write_text("# Site rules\n\nUse pnpm.\n")
    (path / ".claude").mkdir()
    (path / ".claude/settings.json").write_text('{"model": "opus", "permissions": {"allow": ["Bash(pnpm lint)"]}}\n')
    (path / ".codex").mkdir()
    (path / ".codex/config.toml").write_text('model = "gpt-5"\n')
    (path / "supabase/migrations").mkdir(parents=True)
    (path / "supabase/migrations/20260101000000_init.sql").write_text("create table public.t(id int);\n")
    (path / "src").mkdir()
    (path / "src/page.tsx").write_text("export default 1\n")
    env = {**os.environ, **GIT_ENV}
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "init"]):
        subprocess.run(["git", "-C", str(path), *args], check=True, env=env, capture_output=True)
    (path / "src/page.tsx").write_text("export default 2\n")  # an uncommitted change that must survive


class TestInstallSafety(unittest.TestCase):
    def run_check(self, playbook: Path, tmp: Path):
        return subprocess.run([sys.executable, str(CHECK), str(playbook), str(tmp / "out"), str(tmp / "site")],
                              capture_output=True, text=True, env={**os.environ, **GIT_ENV})

    def test_real_installer_passes_every_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            fixture_repo(tmp / "site")
            r = self.run_check(ROOT, tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for mode in ("vendor", "plugin", "full", "no-link"):
                self.assertIn(f"PASS site", r.stdout)
                self.assertRegex(r.stdout, rf"PASS site\s+{mode}\b")
            self.assertEqual((tmp / "site/AGENTS.md").read_text(), "# Site rules\n\nUse pnpm.\n")  # original untouched

    def test_catches_extra_agents_md_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            fixture_repo(tmp / "site")
            bad = tmp / "bad-playbook"
            shutil.copytree(ROOT, bad, ignore=shutil.ignore_patterns(".git", ".superpowers", "__pycache__"))
            src = (bad / "scripts/playbook.py").read_text()
            hook = '            s.append_line("AGENTS.md", POINTER)\n'
            self.assertIn(hook, src)
            (bad / "scripts/playbook.py").write_text(src.replace(
                hook, hook + '            s.append_line("AGENTS.md", "Also: always use tabs.")\n'))
            r = self.run_check(bad, tmp)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("AGENTS.md", r.stdout)
            self.assertIn("FAIL site", r.stdout)


if __name__ == "__main__":
    unittest.main()
