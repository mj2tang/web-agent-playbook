#!/usr/bin/env python3
"""Deterministic design anti-pattern lint (no model, no network). Part of the design-check gate.

  python3 scripts/gates/design_lint.py src/app src/components

Prints `file:line rule message` per finding and exits 1 if there are any. Rules follow the design-tokens,
accessibility-audit, and responsive-layout skills; after Impeccable's detector and the ui-ux-pro-max checklist.
Silence one line only with a reason: `design-lint-ignore: <why>` (reviewers read these).
"""

import re
import sys
from pathlib import Path

EXTS = {".tsx", ".jsx", ".ts", ".js", ".css", ".scss", ".html", ".vue", ".svelte", ".astro", ".mdx"}
SKIP_DIRS = {"node_modules", ".next", "dist", "build", "out", "coverage"}
TOKEN_FILES = re.compile(r"(^|/)(tokens|theme|design-tokens)\.(css|scss|ts|js)$")
PALETTE = ("slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|"
           "violet|purple|fuchsia|pink|rose")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")
IGNORE = re.compile(r"design-lint-ignore(?::\s*(\S.*?))?\s*(?:\*/|-->|$)")

RULES = [
    ("raw-value", re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|oklch)\(|\[(?:-?\d+(?:\.\d+)?(?:px|rem|em)|#[0-9a-fA-F]{3,8})\]"),
     "raw colour or size; use a design token (src/styles/tokens.css) or a Tailwind class that maps to one"),
    ("palette-class", re.compile(rf"\b(?:bg|text|border|ring|fill|stroke|from|via|to|outline|divide|shadow)-(?:{PALETTE})-\d{{2,3}}\b"),
     "default Tailwind palette bypasses the tokens; use a semantic colour (bg-surface, text-muted, bg-accent ...)"),
    ("ai-gradient", re.compile(r"\bfrom-(?:purple|violet|indigo|fuchsia)-\d{2,3}\b[^\"'`]*\bto-(?:pink|blue|purple|indigo|fuchsia)-\d{2,3}\b"),
     "purple/indigo gradient is the generic AI look; take colour from the brief and tokens"),
    ("emoji-icon", EMOJI, "emoji used as an icon; use an SVG icon with an accessible name, or none"),
    ("focus-removed", re.compile(r"\boutline-none\b(?![^\"'`]*\bfocus-visible:)|outline:\s*(?:none|0)\b"),
     "focus indicator removed without a focus-visible replacement (WCAG 2.4.7)"),
    ("clickable-div", re.compile(r"<(?:div|span)\b[^>]*\bonClick="), "clickable div/span; use <button> or <a> for keyboard and screen readers"),
    ("raw-img", re.compile(r"<img\b"), "raw <img>; use next/image (sizes, lazy loading, no layout shift) or add width/height"),
]


def files(roots):
    for root in roots:
        base = Path(root)
        if base.is_file():
            yield base
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in EXTS and not SKIP_DIRS & set(p.parts):
                yield p


def lint_file(path: Path):
    rel = path.as_posix()
    token_file = TOKEN_FILES.search(rel)
    css = path.suffix in {".css", ".scss"}
    for n, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
        ignore = IGNORE.search(line)
        if ignore and (ignore.group(1) or "").strip():
            continue
        code = line.split("//", 1)[0] if not css and "://" not in line else line
        for rule, pattern, message in RULES:
            if rule == "raw-value" and token_file:
                continue
            if rule in ("clickable-div", "raw-img", "emoji-icon") and css:
                continue
            if pattern.search(code):
                yield rel, n, rule, message
        if ignore:
            yield rel, n, "ignore-without-reason", "design-lint-ignore needs a reason: `design-lint-ignore: <why>`"


def main(argv):
    roots = [r for r in argv if Path(r).exists()] or ["src"]
    findings = [f for path in files(roots) for f in lint_file(path)]
    for rel, n, rule, message in findings:
        print(f"{rel}:{n} {rule} {message}")
    print(f"design-lint: {len(findings)} finding{'s' if len(findings) != 1 else ''}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
