# Gates for {{project}}. Agents and CI run the same targets (web-quality-gates skill).
.PHONY: setup env db-start db-stop check design-check db-check ui-check baselines perf

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

# Deterministic design lint (tokens, focus, semantics, generic-AI patterns); fast, so part of check.
design-check:
	scripts/gates/design-check.sh

check: design-check
	pnpm run lint
	pnpm run typecheck
	pnpm run test

db-check: db-start
	pnpm exec supabase db reset
	pnpm exec supabase test db
	pnpm run db:types:check

ui-check: env
	pnpm exec playwright test

# Human step: write missing screenshot baselines, look at them, then commit them. ui-check fails without them.
baselines: env
	UPDATE_BASELINES=1 pnpm exec playwright test --grep @visual

perf: env
	pnpm build
	node scripts/lighthouse-config.mjs
	pnpm dlx @lhci/cli@0.16.0 autorun --config=.lighthouserc.json
