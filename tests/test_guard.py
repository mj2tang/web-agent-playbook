"""Guard hook: blocks, asks, allows, protected paths."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import ROOT  # noqa: E402

GUARD = [sys.executable, str(ROOT / "hooks/scripts/guard.py")]


def guard(mode, tool_input, cwd=None):
    event = {"tool_input": tool_input}
    if cwd:
        event["cwd"] = str(cwd)
    p = subprocess.run([*GUARD, mode], input=json.dumps(event), capture_output=True, text=True)
    decision = None
    if p.returncode == 0 and p.stdout.strip():
        decision = json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"]
    return p.returncode, decision


class TestGuardBash(unittest.TestCase):
    def test_blocks(self):
        for cmd in ["git push origin main", "git -C ../wt push", "git reset --hard HEAD~1",
                    "supabase link --project-ref abc", "pnpm exec supabase db push", "npx supabase db push --linked",
                    "supabase db push --db-url postgresql://u@db.x.supabase.co/postgres",
                    "supabase functions deploy hello", "psql postgresql://u@db.abc.supabase.co:5432/postgres",
                    "vercel --prod", "netlify deploy --prod", "rm -rf ~", "supabase secrets set KEY=v"]:
            self.assertEqual(guard("bash", {"command": cmd})[0], 2, cmd)

    def test_asks(self):
        for cmd in ["pnpm add zod", "npm install lodash", "yarn add x", "npm i react-icons",
                    "pnpm exec playwright test --update-snapshots", "pnpm exec playwright test -u",
                    "supabase migration repair 2024"]:
            self.assertEqual(guard("bash", {"command": cmd}), (0, "ask"), cmd)

    def test_allows(self):
        for cmd in ["pnpm install --frozen-lockfile", "pnpm install", "npm ci", "supabase db reset",
                    "pnpm exec supabase db push --local", "supabase start", "supabase test db", "make db-check",
                    "git commit -m 'T-1: x'", "psql postgresql://postgres:postgres@127.0.0.1:54322/postgres",
                    "pnpm exec playwright test --grep @visual"]:
            self.assertEqual(guard("bash", {"command": cmd}), (0, None), cmd)


class TestGuardFiles(unittest.TestCase):
    def test_protects_paths(self):
        for path in ["/p/.env.local", "/p/.env", "/p/configs/gates.json", "/p/tests/e2e/__screenshots__/home.png",
                     "/p/tests/e2e/home.spec.ts-snapshots/x.png", "/p/supabase/.temp/project-ref"]:
            self.assertEqual(guard("files", {"file_path": path})[0], 2, path)
        self.assertEqual(guard("files", {"file_path": "/p/src/app/page.tsx", "content": "x"}), (0, None))
        self.assertEqual(guard("files", {"file_path": "/p/.env.example", "content": "X="}), (0, None))

    def test_blocks_service_role_in_client_code(self):
        client = '"use client";\nconst k = process.env.SUPABASE_SERVICE_ROLE_KEY\n'
        self.assertEqual(guard("files", {"file_path": "/p/src/app/x/page.tsx", "content": client})[0], 2)
        self.assertEqual(guard("files", {"file_path": "/p/src/app/x/page.tsx",
                                         "new_string": "const k = process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY"})[0], 2)
        server = 'import "server-only";\nconst k = process.env.SUPABASE_SERVICE_ROLE_KEY\n'
        self.assertEqual(guard("files", {"file_path": "/p/src/lib/server/admin.ts", "content": server}), (0, None))

    def test_asks_before_editing_applied_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            mig = repo / "supabase/migrations/20260101000000_a.sql"
            mig.parent.mkdir(parents=True)
            mig.write_text("create table a();\n")
            for args in (["init", "-q"], ["add", "-A"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "a"]):
                subprocess.run(["git", "-C", tmp, *args], check=True, capture_output=True)
            self.assertEqual(guard("files", {"file_path": str(mig), "new_string": "x"}, cwd=repo), (0, "ask"))
            new = repo / "supabase/migrations/20260102000000_b.sql"
            self.assertEqual(guard("files", {"file_path": str(new), "content": "x"}, cwd=repo), (0, None))


if __name__ == "__main__":
    unittest.main()
