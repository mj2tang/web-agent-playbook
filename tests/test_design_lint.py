"""design_lint.py: deterministic design anti-pattern rules (after Impeccable's detector and ui-ux-pro-max's checklist)."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import ROOT  # noqa: E402

LINT = ROOT / "templates/agent-config/scripts/gates/design_lint.py"


def lint(files: dict[str, str]):
    with tempfile.TemporaryDirectory() as tmp:
        for rel, text in files.items():
            p = Path(tmp) / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        r = subprocess.run([sys.executable, str(LINT), "src"], cwd=tmp, capture_output=True, text=True)
        return r.returncode, r.stdout


class TestDesignLint(unittest.TestCase):
    def rules(self, text, path="src/app/page.tsx"):
        rc, out = lint({path: text})
        return rc, {line.split()[1] for line in out.splitlines() if line.startswith("src/")}

    def test_clean_component_passes(self):
        rc, out = lint({"src/app/page.tsx": '<button className="rounded-md bg-accent px-4 py-2 text-accent-fg '
                                            'focus-visible:outline-2">Save note</button>\n'})
        self.assertEqual((rc, out.strip()), (0, "design-lint: 0 findings"))

    def test_raw_colours_and_arbitrary_values(self):
        self.assertEqual(self.rules('<p className="text-[#3b82f6] p-[13px]">x</p>')[1], {"raw-value"})
        self.assertEqual(self.rules('<p style={{ color: "rgb(1,2,3)" }}>x</p>')[1], {"raw-value"})
        self.assertEqual(self.rules(".x { color: #fff; }", "src/components/x.css")[1], {"raw-value"})

    def test_tokens_file_may_hold_raw_values(self):
        self.assertEqual(self.rules(":root { --color-bg: #fff; }", "src/styles/tokens.css"), (0, set()))

    def test_default_palette_and_ai_gradient(self):
        self.assertIn("palette-class", self.rules('<div className="bg-blue-500">x</div>')[1])
        self.assertIn("ai-gradient", self.rules('<div className="bg-gradient-to-r from-purple-500 to-pink-500">x</div>')[1])

    def test_emoji_icons(self):
        self.assertEqual(self.rules("<span>🚀 Launch</span>")[1], {"emoji-icon"})

    def test_focus_removed(self):
        self.assertEqual(self.rules('<a className="outline-none">x</a>')[1], {"focus-removed"})
        self.assertEqual(self.rules('<a className="outline-none focus-visible:ring-2">x</a>'), (0, set()))
        self.assertEqual(self.rules("a:focus { outline: none; }", "src/app/x.css")[1], {"focus-removed"})

    def test_clickable_div_and_raw_img(self):
        self.assertEqual(self.rules("<div onClick={go}>x</div>")[1], {"clickable-div"})
        self.assertEqual(self.rules('<img src="/a.png" />')[1], {"raw-img"})

    def test_ignore_needs_a_reason(self):
        self.assertEqual(self.rules('<p className="bg-blue-500">x</p> {/* design-lint-ignore: brand partner logo colour */}'),
                         (0, set()))
        self.assertEqual(self.rules('<p className="bg-blue-500">x</p> {/* design-lint-ignore */}')[1],
                         {"palette-class", "ignore-without-reason"})

    def test_output_is_file_line_rule(self):
        rc, out = lint({"src/app/page.tsx": "ok\n<div onClick={go}>x</div>\n"})
        self.assertEqual(rc, 1)
        self.assertIn("src/app/page.tsx:2 clickable-div", out)


if __name__ == "__main__":
    unittest.main()
