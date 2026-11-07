# Gates for {{project}}. Agents and CI run the same targets (web-quality-gates skill).
.PHONY: setup env db-start db-stop check db-check ui-check perf

setup:
	pnpm install
	pnpm exec playwright install chromium

# Local Supabase (Docker). Never link or push from here.
db-start:
	pnpm exec supabase status >/dev/null 2>&1 || pnpm exec supabase start

db-stop:
	pnpm exec supabase stop

# .env.local from the running local stack.
env: db-start
	scripts/env-local.sh

check:
	pnpm run lint
	pnpm run typecheck
	pnpm run test

db-check: db-start
	pnpm exec supabase db reset
	pnpm exec supabase test db
	pnpm run db:types:check

ui-check: env
	pnpm exec playwright test

perf: env
	pnpm build
	pnpm dlx @lhci/cli@0.16.0 autorun --config=lighthouserc.json
