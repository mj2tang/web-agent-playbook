"""playbook.py doctor: health check of an installed project (after oh-my-codex `omx doctor` and ECC doctor)."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import PLAYBOOK, run_playbook as run  # noqa: E402


def doctor(path, env=None):
    p = subprocess.run([*PLAYBOOK, "doctor", str(path)], capture_output=True, text=True,
                       env={**os.environ, **(env or {})})
    return p.returncode, p.stdout


class TestDoctor(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_no_install(self):
        rc, out = doctor(self.repo)
        self.assertEqual(rc, 1)
        self.assertIn("run `playbook.py init`", out)

    def test_healthy_install(self):
        run("init", str(self.repo), "--guardrails")
        rc, out = doctor(self.repo)
        self.assertEqual(rc, 0, out)
        self.assertIn("OK   managed files", out)
        self.assertIn("OK   claude hooks", out)
        self.assertIn("OK   codex hooks", out)
        self.assertIn("/hooks", out)  # trust reminder: untrusted Codex hooks don't run
        self.assertIn("OK   codex agents: 9", out)

    def test_missing_managed_file_fails_and_edit_warns(self):
        run("init", str(self.repo))
        (self.repo / "scripts/gates/check.sh").unlink()
        skill = self.repo / ".agents/skills/tdd-loop/SKILL.md"
        skill.write_text(skill.read_text() + "\nlocal\n")
        rc, out = doctor(self.repo)
        self.assertEqual(rc, 1, out)
        self.assertIn("FAIL managed files: 1 missing (scripts/gates/check.sh)", out)
        self.assertIn("1 edited locally", out)
        self.assertIn("playbook.py sync", out)

    def test_guard_without_claude_hook_registration_fails(self):
        run("init", str(self.repo), "--guardrails")
        settings = self.repo / ".claude/settings.json"
        data = json.loads(settings.read_text())
        data.pop("hooks")
        settings.write_text(json.dumps(data))
        rc, out = doctor(self.repo)
        self.assertEqual(rc, 1)
        self.assertIn("FAIL claude hooks", out)

    def test_supabase_project_without_cli_warns(self):
        (self.repo / "supabase").mkdir()
        run("init", str(self.repo))
        rc, out = doctor(self.repo, env={"PATH": "/usr/bin:/bin"})
        self.assertIn("WARN supabase CLI", out)


if __name__ == "__main__":
    unittest.main()
