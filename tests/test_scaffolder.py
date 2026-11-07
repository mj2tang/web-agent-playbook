"""Scaffolder: init into existing repos, sync, and (Task 8) new."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import PLAYBOOK, ROOT, run_playbook as run  # noqa: E402

POINTER = "See AGENTS.web-playbook.md for the web agent team's rules, gates, and approvals; read it before any task."


class TestInit(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_layout(self):
        run("init", str(self.repo), "--name", "legacy")
        for rel in [".agents/skills/worker-protocol/SKILL.md", ".agents/skills/design-tokens/SKILL.md",
                    ".claude/agents/orchestrator.md", ".claude/agents/system-architect.md", "tasks/BOARD.md",
                    "scripts/agent-team/run-wave.sh", "scripts/gates/check.sh", "scripts/gates/lib.sh",
                    "docs/pipeline-map/routes.md", "configs/team.json", "configs/gates.json",
                    "AGENTS.web-playbook.md", ".agents/web-playbook.lock.json", ".codex/config.toml"]:
            self.assertTrue((self.repo / rel).exists(), rel)
        self.assertTrue((self.repo / ".claude/skills").is_symlink())
        self.assertNotIn("{{", (self.repo / "AGENTS.web-playbook.md").read_text())
        self.assertIn("legacy", (self.repo / "AGENTS.web-playbook.md").read_text())
        self.assertNotIn("{{", (self.repo / ".codex/config.toml").read_text())
        settings = json.loads((self.repo / ".claude/settings.json").read_text())
        self.assertIn("Bash(scripts/gates/check.sh)", settings["permissions"]["allow"])
        self.assertNotIn("hooks", settings)  # guardrails are opt-in for existing repos

    def test_init_appends_pointer_once(self):
        (self.repo / "AGENTS.md").write_bytes(b"# mine")
        run("init", str(self.repo))
        expected = ("# mine\n\n" + POINTER + "\n").encode()
        self.assertEqual((self.repo / "AGENTS.md").read_bytes(), expected)
        run("init", str(self.repo))
        self.assertEqual((self.repo / "AGENTS.md").read_bytes(), expected)

    def test_init_crlf_agents_md(self):
        (self.repo / "AGENTS.md").write_bytes(b"# mine\r\nrules\r\n")
        run("init", str(self.repo))
        data = (self.repo / "AGENTS.md").read_bytes()
        self.assertTrue(data.startswith(b"# mine\r\nrules\r\n"))
        self.assertEqual(data, b"# mine\r\nrules\r\n\r\n" + POINTER.encode() + b"\r\n")

    def test_init_no_link(self):
        (self.repo / "AGENTS.md").write_text("# mine\n")
        run("init", str(self.repo), "--no-link")
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "# mine\n")

    def test_init_creates_agents_md_when_absent(self):
        run("init", str(self.repo))
        self.assertEqual((self.repo / "AGENTS.md").read_text(), POINTER + "\n")
        self.assertEqual((self.repo / "CLAUDE.md").read_text(), "@AGENTS.web-playbook.md\n")

    def test_init_leaves_existing_claude_md(self):
        (self.repo / "CLAUDE.md").write_text("# my rules\n")
        out = run("init", str(self.repo))
        self.assertEqual((self.repo / "CLAUDE.md").read_text(), "# my rules\n")
        self.assertIn("@AGENTS.web-playbook.md", out)  # tells the user how to link it

    def test_init_refuses_alongside_ml_playbook(self):
        (self.repo / ".agents").mkdir()
        (self.repo / ".agents/playbook.lock.json").write_text("{}")
        p = subprocess.run([*PLAYBOOK, "init", str(self.repo)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("coding-agent-playbook", p.stdout)
        self.assertFalse((self.repo / ".claude").exists())

    def test_init_codex_config_sidecar(self):
        (self.repo / ".codex").mkdir()
        (self.repo / ".codex/config.toml").write_text('model = "mine"\n')
        out = run("init", str(self.repo))
        self.assertEqual((self.repo / ".codex/config.toml").read_text(), 'model = "mine"\n')
        self.assertTrue((self.repo / ".codex/web-playbook.config.toml").exists())
        self.assertIn("[mcp_servers.playwright]", out)

    def test_profile_auto_supabase(self):
        run("init", str(self.repo))
        self.assertFalse((self.repo / ".agents/skills/rls-policies").exists())
        self.assertFalse((self.repo / "supabase").exists())
        (self.repo / "supabase").mkdir()
        run("init", str(self.repo))
        self.assertTrue((self.repo / ".agents/skills/rls-policies/SKILL.md").exists())
        self.assertTrue((self.repo / "supabase/tests/rls_enabled.test.sql").exists())

    def test_init_never_touches_package_json(self):
        pkg = b'{"name":"x","scripts":{"lint":"eslint ."}}'
        (self.repo / "package.json").write_bytes(pkg)
        (self.repo / "pnpm-lock.yaml").write_text("")
        out = run("init", str(self.repo), "--profile", "ui")
        self.assertEqual((self.repo / "package.json").read_bytes(), pkg)
        self.assertTrue((self.repo / "playwright.playbook.config.ts").exists())
        self.assertTrue((self.repo / "tests/e2e-playbook/a11y.spec.ts").exists())
        self.assertIn("pnpm add -D @playwright/test @axe-core/playwright", out)

    def test_guardrails_opt_in(self):
        run("init", str(self.repo), "--guardrails")
        settings = json.loads((self.repo / ".claude/settings.json").read_text())
        self.assertIn("PreToolUse", settings["hooks"])
        self.assertTrue((self.repo / ".claude/hooks/guard.py").exists())
        self.assertIn("Bash(git -C:*)", settings["permissions"]["allow"])

    def test_init_preserves_settings(self):
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude/settings.json").write_text('{"model": "opus", "permissions": {"allow": ["Bash(x)"]}}')
        run("init", str(self.repo))
        settings = json.loads((self.repo / ".claude/settings.json").read_text())
        self.assertEqual(settings["model"], "opus")
        self.assertIn("Bash(x)", settings["permissions"]["allow"])

    def test_plugin_mode(self):
        run("init", str(self.repo), "--mode", "plugin")
        settings = json.loads((self.repo / ".claude/settings.json").read_text())
        self.assertTrue(settings["enabledPlugins"]["web-playbook@mj2tang"])
        self.assertFalse((self.repo / ".claude/agents").exists())
        self.assertTrue((self.repo / ".agents/skills/tdd-loop/SKILL.md").exists())


class TestSync(unittest.TestCase):
    def test_sync_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("init", tmp)
            self.assertIn("0 created, 0 updated, 0 skipped", run("sync", tmp))

    def test_sync_keeps_edits_and_restores_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("init", tmp)
            skill = Path(tmp) / ".agents/skills/tdd-loop/SKILL.md"
            skill.write_text(skill.read_text() + "\nlocal rule\n")
            gone = Path(tmp) / ".agents/skills/ux-copy/SKILL.md"
            gone.unlink()
            out = run("sync", tmp)
            self.assertIn("1 created", out)
            self.assertIn("1 skipped", out)
            self.assertIn("local rule", skill.read_text())
            self.assertTrue(gone.exists())

    def test_sync_does_not_add_supabase_skills_to_non_supabase_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("init", tmp)
            run("sync", tmp)
            self.assertFalse((Path(tmp) / ".agents/skills/rls-policies").exists())


if __name__ == "__main__":
    unittest.main()


class TestNew(unittest.TestCase):
    def test_new_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "site"
            run("new", str(proj), "--name", "Acme Notes")
            for rel in ["AGENTS.md", "CLAUDE.md", "Makefile", "package.json", "next.config.ts", "tsconfig.json",
                        "playwright.config.ts", "vitest.config.mts", "src/styles/tokens.css", "src/app/layout.tsx",
                        "src/app/notes/actions.ts", "src/lib/supabase/server.ts", "src/proxy.ts",
                        "src/lib/contracts/notes.ts", "supabase/config.toml", "supabase/tests/rls_enabled.test.sql",
                        "supabase/tests/notes_rls.test.sql", "tests/e2e/a11y.spec.ts", ".github/workflows/ci.yml",
                        ".claude/agents/supervisor.md", ".claude/hooks/guard.py", ".agents/skills/rls-policies/SKILL.md",
                        ".codex/config.toml", "scripts/gates/check.sh", "docs/pipeline-map/routes.md",
                        ".agents/web-playbook.lock.json"]:
                self.assertTrue((proj / rel).exists(), rel)
            self.assertFalse((proj / "AGENTS.web-playbook.md").exists())
            self.assertFalse((proj / "playwright.playbook.config.ts").exists())
            for rel in ["AGENTS.md", "package.json", "supabase/config.toml", "src/app/layout.tsx", "README.md",
                        "Makefile", ".codex/config.toml"]:
                self.assertNotRegex((proj / rel).read_text(), r"\{\{\w+\}\}", rel)  # unrendered placeholders
            self.assertIn("BEGIN:nextjs-agent-rules", (proj / "AGENTS.md").read_text())
            self.assertEqual(json.loads((proj / "package.json").read_text())["name"], "acme-notes")
            self.assertIn('project_id = "acme-notes"', (proj / "supabase/config.toml").read_text())
            settings = json.loads((proj / ".claude/settings.json").read_text())
            self.assertIn("Bash(make db-check)", settings["permissions"]["allow"])
            self.assertIn("PreToolUse", settings["hooks"])
            self.assertIn(".audit/", (proj / ".gitignore").read_text())
            log = subprocess.run(["git", "-C", str(proj), "log", "--oneline"], capture_output=True, text=True)
            self.assertIn("Scaffold Acme Notes", log.stdout)

    def test_new_refuses_non_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "x").write_text("x")
            p = subprocess.run([*PLAYBOOK, "new", tmp, "--name", "x"], capture_output=True, text=True)
            self.assertEqual(p.returncode, 1)
