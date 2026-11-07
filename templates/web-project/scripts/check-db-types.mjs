// Fails if src/lib/database.types.ts is out of date with the local database (run after `supabase db reset`).
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

const file = "src/lib/database.types.ts";
const generated = execFileSync("supabase", ["gen", "types", "typescript", "--local"], { encoding: "utf8" });
const committed = readFileSync(file, "utf8");
if (generated.trim() !== committed.trim()) {
  console.error(`${file} is out of date. Run \`pnpm run db:types\` and commit the result.`);
  process.exit(1);
}
console.log(`${file} matches the local schema.`);
