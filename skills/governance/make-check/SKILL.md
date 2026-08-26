---
name: make-check
description: Use before running any build, test, lint, format, or validation. Find and run the canonical Make verb instead of ad-hoc tool invocations that bypass guards, locks, and evidence. The Makefile is the source of truth for how to validate.
bundle: governance
scope: universal
license: MIT
metadata:
  version: 1.0.0
---

# Make Check

In FLEXT/ai-hub every gate runs through canonical Make verbs (generated from
`base.mk`), never raw `ruff`/`pytest`/`uv` calls that skip guards, locks, dry-run
semantics, and evidence. Ad-hoc test scripts are forbidden; theories become
strict tests under `tests/`. Find the verb before you run anything.

## Use for

- Choosing the correct target for build / test / lint / format / validate.
- Any "how do I check this" moment.

## Do not use for

- Inventing targets that do not exist.
- Running destructive targets without operator confirmation.

## Canonical verbs (ai-hub / FLEXT projects)

- `make setup` — env bootstrap (mise + uv venv + sync).
- `make check CHECK_GATES=lint,format,pyrefly,mypy,pyright [FILES=...]` — the DoD
  gate; add `FILES=`/`CHANGED_ONLY=1` for the fast per-file path.
- `make test [PYTEST_ARGS=...]` — pytest (pytest `--timeout=10` is standard).
- `make build` — artifacts + golden.
- `make val VALIDATE_GATES=...` — extra validation. `make fmt` — format.

## Workflow

1. From the project root, run `make help`.
2. Pick the closest verb; prefer the fast `FILES=`/`CHANGED_ONLY=1` path for scoped work.
3. Run it; capture command, working dir, exit code, decisive output.
4. A broken canonical verb is fixed at its owner first — never routed around.

## Critical rules

- Run per-project from that project's root; never couple workspaces.
- Green means real, fresh, timestamped evidence — not a claim.
