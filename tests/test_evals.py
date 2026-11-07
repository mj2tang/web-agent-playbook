"""Skill-routing eval cases and the blinded skill A/B harness (scripts/skill_eval.py)."""

import importlib.util
import json
import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import ROOT  # noqa: E402


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestRoutingCases(unittest.TestCase):
    def test_every_skill_has_a_routing_case_and_lines_parse(self):
        cases = [json.loads(line) for line in (ROOT / "evals/skill-routing.jsonl").read_text().splitlines() if line]
        skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        expected = {c["expect"] for c in cases}
        self.assertEqual(skills - expected, set(), "skills without a routing case")
        self.assertEqual(expected - skills - {None}, set(), "cases naming unknown skills")
        self.assertIn(None, expected, "include near-miss cases where no skill should load")


class TestSkillEval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_eval = load(ROOT / "scripts/skill_eval.py", "skill_eval")

    def test_blinding_rejects_meta_prompts(self):
        for bad in ["This is an eval of your skills", "You are being graded on this", "use the rubric"]:
            with self.assertRaises(ValueError):
                self.skill_eval.check_blind(bad, "prompt")
        self.skill_eval.check_blind("Add an archive button to the notes page with tests", "prompt")

    def test_project_names_are_neutral(self):
        for name in self.skill_eval.PROJECT_NAMES:
            self.skill_eval.check_blind(name, "project name")

    def test_summarise_unblinds_by_mapping(self):
        scores = {"Submission 1": {"tests": 5, "scope": 4, "notes": "x"}, "Submission 2": {"tests": 1, "scope": 2}}
        summary = self.skill_eval.summarise(scores, {"Submission 1": "B", "Submission 2": "A"})
        self.assertEqual(summary["B"]["total"], 9.0)
        self.assertEqual(summary["A"]["tests"], 1.0)

    def test_end_to_end_with_fake_runner_and_judge(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            a = tmp / "a" / "tdd-loop"
            b = tmp / "b" / "tdd-loop"
            shutil.copytree(ROOT / "skills/tdd-loop", a)
            shutil.copytree(ROOT / "skills/tdd-loop", b)
            (b / "SKILL.md").write_text((b / "SKILL.md").read_text() + "\nMARKER-WRITE-TESTS\n")
            runner = tmp / "runner.py"
            # Behaves "better" (writes a test file) only when the installed skill has the marker.
            runner.write_text(textwrap.dedent("""
                import pathlib, sys
                task = sys.stdin.read()
                skill = pathlib.Path('.agents/skills/tdd-loop/SKILL.md').read_text()
                pathlib.Path('NOTES.md').write_text(task)
                if 'MARKER-WRITE-TESTS' in skill:
                    pathlib.Path('tests/unit/new-thing.test.ts').write_text('import { it } from "vitest";\\nit("x", () => {});\\n')
                print('done')
            """))
            judge = tmp / "judge.py"
            judge.write_text(textwrap.dedent("""
                import json, re, sys
                text = sys.stdin.read()
                blocks = re.split(r'\\n===== (Submission \\d+) =====\\n', text)[1:]
                out = {}
                for label, body in zip(blocks[::2], blocks[1::2]):
                    out[label] = {"tests": 5 if 'new-thing.test.ts' in body else 1, "notes": "ok"}
                print(json.dumps(out))
            """))
            prompt = tmp / "prompt.txt"
            prompt.write_text("Add a word count under each note on the notes page.")
            rubric = tmp / "rubric.md"
            rubric.write_text("- tests: new behaviour has a test")
            out = tmp / "out"
            rc = self.skill_eval.main(["--skill", "tdd-loop", "--variant-a", str(a), "--variant-b", str(b),
                                       "--prompt-file", str(prompt), "--rubric", str(rubric), "--runs", "2",
                                       "--runner", f"{sys.executable} {runner}", "--judge",
                                       f"{sys.executable} {judge}", "--out", str(out), "--seed", "1"])
            self.assertEqual(rc, 0)
            mapping = json.loads((out / "tdd-loop/mapping.json").read_text())
            self.assertEqual(sorted(m["variant"] for m in mapping.values()), ["A", "A", "B", "B"])
            report = (out / "tdd-loop/report.md").read_text()
            self.assertIn("| A | 1.00 | 1.00 |", report)
            self.assertIn("| B | 5.00 | 5.00 |", report)


if __name__ == "__main__":
    unittest.main()
