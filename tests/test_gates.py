"""Gate scripts (templates/agent-config/scripts/gates): package-manager detection, discovery, SKIPPED."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import ROOT  # noqa: E402

GATES = ROOT / "templates/agent-config/scripts/gates"


class GateCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        subprocess.run(["cp", "-R", str(GATES), str(self.repo / "scripts/gates")], check=True)
        self.bin = Path(self._tmp.name) / "bin"
        self.bin.mkdir()
        self.calls = Path(self._tmp.name) / "calls"
        for pm in ("pnpm", "npm", "yarn", "bun", "npx"):
            f = self.bin / pm
            f.write_text(f'#!/bin/sh\necho "{pm} $*" >> "$CALLS"\n')
            f.chmod(0o755)

    def tearDown(self):
        self._tmp.cleanup()

    def package(self, scripts, lock="pnpm-lock.yaml"):
        (self.repo / "package.json").write_text(json.dumps({"name": "x", "scripts": scripts}))
        if lock:
            (self.repo / lock).write_text("")

    def gate(self, name, **env):
        e = {**os.environ, "PATH": f"{self.bin}:/usr/bin:/bin", "CALLS": str(self.calls), **env}
        e.pop("GATES_ALLOW_SKIP", None) if "GATES_ALLOW_SKIP" not in env else None
        p = subprocess.run(["bash", f"scripts/gates/{name}.sh"], cwd=self.repo, env=e, capture_output=True, text=True)
        calls = self.calls.read_text() if self.calls.exists() else ""
        return p.returncode, p.stdout + p.stderr, calls


class TestGates(GateCase):
    def test_pm_detection(self):
        for lock, pm in (("pnpm-lock.yaml", "pnpm"), ("package-lock.json", "npm"), ("yarn.lock", "yarn"),
                         ("bun.lock", "bun"), (None, "npm")):
            for f in ("pnpm-lock.yaml", "package-lock.json", "yarn.lock", "bun.lock"):
                (self.repo / f).unlink(missing_ok=True)
            self.package({"lint": "x", "typecheck": "x", "test": "x"}, lock=lock)
            self.calls.unlink(missing_ok=True)
            rc, out, calls = self.gate("check")
            self.assertEqual(rc, 0, out)
            self.assertIn(f"{pm} run lint", calls, lock)

    def test_check_runs_repo_scripts(self):
        self.package({"lint": "x", "typecheck": "x", "test": "x"})
        rc, out, calls = self.gate("check")
        self.assertEqual(rc, 0, out)
        self.assertEqual(calls.splitlines(), ["pnpm run lint", "pnpm run typecheck", "pnpm run test"])

    def test_typecheck_falls_back_to_tsc(self):
        self.package({"lint": "x", "test": "x"})
        (self.repo / "tsconfig.json").write_text("{}")
        rc, out, calls = self.gate("check")
        self.assertEqual(rc, 0, out)
        self.assertIn("pnpm exec tsc --noEmit", calls)

    def test_missing_script_is_skipped_not_passed(self):
        self.package({"typecheck": "x", "test": "x"})
        rc, out, _ = self.gate("check")
        self.assertIn('SKIPPED: lint (no "lint" script in package.json)', out)
        self.assertEqual(rc, 4)
        rc, _, _ = self.gate("check", GATES_ALLOW_SKIP="1")
        self.assertEqual(rc, 0)

    def test_failure_is_failure(self):
        self.package({"lint": "x", "typecheck": "x", "test": "x"})
        (self.bin / "pnpm").write_text('#!/bin/sh\n[ "$2" = "typecheck" ] && exit 1\nexit 0\n')
        rc, out, _ = self.gate("check")
        self.assertEqual(rc, 1, out)
        self.assertIn("FAIL: typecheck", out)

    def test_db_check_skipped_without_supabase(self):
        self.package({})
        rc, out, _ = self.gate("db-check")
        self.assertEqual(rc, 4)
        self.assertIn("SKIPPED: db-check (no supabase/ directory)", out)

    def test_db_check_runs_supabase_locally(self):
        self.package({"db:types:check": "x"})
        (self.repo / "supabase/tests").mkdir(parents=True)
        rc, out, calls = self.gate("db-check")
        self.assertEqual(rc, 0, out)
        self.assertIn("pnpm exec supabase db reset", calls)
        self.assertIn("pnpm exec supabase test db", calls)
        self.assertNotIn("--linked", calls)

    def test_ui_check_skipped_without_playwright_config(self):
        self.package({})
        rc, out, _ = self.gate("ui-check")
        self.assertEqual(rc, 4)
        self.assertIn("SKIPPED: ui-check (no Playwright config)", out)

    def test_ui_check_prefers_playbook_config(self):
        self.package({})
        (self.repo / "playwright.config.ts").write_text("")
        (self.repo / "playwright.playbook.config.ts").write_text("")
        rc, out, calls = self.gate("ui-check")
        self.assertEqual(rc, 0, out)
        self.assertIn("pnpm exec playwright test --config playwright.playbook.config.ts", calls)


if __name__ == "__main__":
    unittest.main()
