// Writes .lighthouserc.json from configs/gates.json so performance budgets have one source (make perf).
import { readFileSync, writeFileSync } from "node:fs";

const { perf } = JSON.parse(readFileSync("configs/gates.json", "utf8"));
const base = process.env.PERF_BASE_URL ?? "http://localhost:3000";
const config = {
  ci: {
    collect: { startServerCommand: "pnpm start", url: perf.routes.map((r) => base + r), numberOfRuns: 1 },
    assert: {
      assertions: {
        "largest-contentful-paint": ["error", { maxNumericValue: perf["largest-contentful-paint"] }],
        "cumulative-layout-shift": ["error", { maxNumericValue: perf["cumulative-layout-shift"] }],
        "total-blocking-time": ["error", { maxNumericValue: perf["total-blocking-time"] }],
        "categories:accessibility": ["error", { minScore: perf.accessibility_min_score }],
      },
    },
  },
};
writeFileSync(".lighthouserc.json", JSON.stringify(config, null, 2) + "\n");
console.log(`wrote .lighthouserc.json for ${perf.routes.length} route(s) from configs/gates.json`);
