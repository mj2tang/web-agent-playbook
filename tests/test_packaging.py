"""Manifests, skills, agents, and content rules.

Run: python3 -m unittest discover -s tests -v
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import ROOT, frontmatter  # noqa: E402

ML_TERMS = re.compile(r"mlflow|leakage|rebaseline|champion|databricks|uv sync", re.I)
MIN_SKILLS = 32


class TestPackaging(unittest.TestCase):
    def test_manifests_valid_and_versions_match(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        for f in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json", "hooks/hooks.json"):
            json.loads((ROOT / f).read_text())
        self.assertEqual(claude["version"], "0.1.0")
        self.assertEqual(codex["version"], "0.1.0")
        self.assertEqual(claude["name"], "web-playbook")
        self.assertEqual(codex["name"], "web-playbook")

    def test_skills_frontmatter(self):
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skills), MIN_SKILLS)
        for path in skills:
            fm = frontmatter(path)
            self.assertEqual(fm["name"], path.parent.name)
            self.assertIn("Use ", fm["description"], path)
            self.assertIn("Not ", fm["description"], path)
            self.assertLess(len(fm["description"]), 1024, path)

    def test_agents_reference_existing_skills(self):
        skill_names = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        for path in (ROOT / "agents").glob("*.md"):
            fm = frontmatter(path)
            self.assertEqual(fm["name"], path.stem)
            for skill in re.findall(r"[\w-]+", fm.get("skills", "")):
                self.assertIn(skill, skill_names, f"{path.name} preloads unknown skill {skill}")

    def test_no_ml_content(self):
        hits = []
        for top in ("skills", "agents", "templates"):
            for path in (ROOT / top).rglob("*"):
                if path.is_file() and "node_modules" not in path.parts:
                    for n, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
                        if ML_TERMS.search(line):
                            hits.append(f"{path.relative_to(ROOT)}:{n}: {line.strip()[:80]}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()


class TestDesignContextFiles(unittest.TestCase):
    """PRODUCT.md + DESIGN.md at the repo root: the convention Impeccable, gstack and ui-ux-pro-max share."""

    def test_brief_writes_product_and_design_md(self):
        skill = (ROOT / "skills/design-brief/SKILL.md").read_text()
        self.assertIn("PRODUCT.md", skill)
        self.assertIn("DESIGN.md", skill)
        for name in ("PRODUCT-template.md", "DESIGN-template.md"):
            self.assertTrue((ROOT / "skills/design-brief/assets" / name).exists(), name)

    def test_no_stale_brief_path(self):
        stale = []
        for top in ("skills", "agents", "templates", "docs", "README.md"):
            for path in [ROOT / top] if (ROOT / top).is_file() else (ROOT / top).rglob("*.md"):
                if "superpowers" not in path.parts and "docs/design/brief.md" in path.read_text():
                    stale.append(str(path.relative_to(ROOT)))
        self.assertEqual(stale, [])


class TestWebMode(unittest.TestCase):
    """web-mode: a router with playbooks and a principles index (after Lauren Tan's pstack poteto-mode)."""

    MODE = ROOT / "skills/web-mode"
    PLAYBOOKS = ["investigation", "bug-fix", "feature", "refactoring", "prototype", "visual-parity", "perf-issue", "team"]

    def test_every_playbook_exists_is_listed_and_ends_with_a_reply(self):
        skill = (self.MODE / "SKILL.md").read_text()
        for name in self.PLAYBOOKS:
            path = self.MODE / f"playbooks/{name}.md"
            self.assertTrue(path.exists(), name)
            self.assertIn(f"playbooks/{name}.md", skill, name)
            text = path.read_text()
            self.assertRegex(text, r"(?m)^1\. ", name)
            self.assertIn("**Reply:**", text, name)
        self.assertEqual(sorted(p.stem for p in (self.MODE / "playbooks").glob("*.md")), sorted(self.PLAYBOOKS))

    def test_explicit_invocation_only_in_both_harnesses(self):
        self.assertEqual(frontmatter(self.MODE / "SKILL.md").get("disable-model-invocation"), "true")
        self.assertIn("allow_implicit_invocation: false", (self.MODE / "agents/openai.yaml").read_text())

    def test_principles_index_and_agents_md(self):
        skill = (self.MODE / "SKILL.md").read_text()
        for principle in ("Smallest change", "Build the lever", "Attack the premise", "Explain the number",
                          "Never block on the human", "Guard the context window"):
            self.assertIn(principle, skill, principle)
        self.assertIn("## Principles", (ROOT / "templates/agent-config/AGENTS.md").read_text())

    def test_playbooks_name_existing_skills(self):
        skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        text = "\n".join(p.read_text() for p in (self.MODE / "playbooks").glob("*.md"))
        for name in re.findall(r"\(skill `([a-z-]+)`\)", text):
            self.assertIn(name, skills, name)
