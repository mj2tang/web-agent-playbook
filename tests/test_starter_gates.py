"""Starter gate wiring: thresholds come from configs/gates.json; baselines are written only on purpose (review I4, I5)."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import ROOT  # noqa: E402

WEB = ROOT / "templates/web-project"
GATES = ROOT / "templates/agent-config/configs/gates.json"


@unittest.skipUnless(shutil.which("node"), "node not installed")
class TestLighthouseConfig(unittest.TestCase):
    def test_i4_lighthouse_assertions_come_from_gates_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "configs").mkdir()
            gates = json.loads(GATES.read_text())
            gates["perf"]["largest-contentful-paint"] = 1234
            gates["perf"]["routes"] = ["/", "/pricing"]
            (tmp / "configs/gates.json").write_text(json.dumps(gates))
            (tmp / "scripts").mkdir()
            shutil.copy(WEB / "scripts/lighthouse-config.mjs", tmp / "scripts/")
            subprocess.run(["node", "scripts/lighthouse-config.mjs"], cwd=tmp, check=True, capture_output=True)
            cfg = json.loads((tmp / ".lighthouserc.json").read_text())["ci"]
            self.assertEqual(cfg["assert"]["assertions"]["largest-contentful-paint"], ["error", {"maxNumericValue": 1234}])
            self.assertEqual(cfg["collect"]["url"], ["http://localhost:3000/", "http://localhost:3000/pricing"])


class TestStarterWiring(unittest.TestCase):
    def test_i4_thresholds_read_from_gates_json(self):
        self.assertFalse((WEB / "lighthouserc.json").exists())
        self.assertIn("configs/gates.json", (WEB / "playwright.config.ts").read_text())
        self.assertIn("configs/gates.json", (WEB / "tests/e2e/a11y.spec.ts").read_text())
        self.assertIn("configs/gates.json", (ROOT / "templates/profiles/ui/tests/e2e-playbook/a11y.spec.ts").read_text())
        self.assertIn("lighthouse-config.mjs", (WEB / "Makefile").read_text())

    def test_i5_baselines_only_on_purpose(self):
        cfg = (WEB / "playwright.config.ts").read_text()
        self.assertIn('process.env.UPDATE_BASELINES === "1" ? "missing" : "none"', cfg)
        self.assertNotIn('updateSnapshots: "missing"', cfg)
        mk = (WEB / "Makefile").read_text()
        self.assertIn("baselines:", mk)
        self.assertIn("UPDATE_BASELINES=1", mk)


if __name__ == "__main__":
    unittest.main()
