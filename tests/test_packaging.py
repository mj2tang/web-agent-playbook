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
