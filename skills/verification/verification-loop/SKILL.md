---
name: verification-loop
description: Use at every completion boundary before claiming work done. Run the continuous-green gate in order (env, lint/format, static analysis, types for changed scope, tests, real-artifact use) and stop on the first red. Prevents evidence-less "done".
bundle: verification
scope: universal
license: MIT
metadata:
  version: 1.0.0
---

# Verification Loop

"Done" requires fresh, real, timestamped green — not a claim. Run the gate in order; any later edit invalidates earlier evidence. Use before declaring a task/slice complete and before staging, committing, or handing off a PR. Stop on first red; fix at the owner.

## Completion Gate

Stop on first red; fix at the owner.

1. **Env/bootstrap health** — the venv and toolchain resolve.
2. **Lint + format** — global (`make check` lint,format).
3. **Static analysis** — `pyrefly` (baseline).
4. **Types for changed scope** — `pyrefly` + `mypy` + `pyright` on every changed
   file AND affected consumers (`make check CHECK_GATES=... FILES=...`).
5. **Tests** — `make test` for changed behavior; 0 failed / 0 errors; a test >10s is a defect. Impact selection (testmon) is authoritative: a green selected run closes this phase — re-running the full suite to double-check is the forbidden hand-repeat (UNIVERSAL_CORE Law 7). Full suite = CI or explicit operator request only.
6. **Real-artifact use** — import/run the actual surface (CLI, daemon, `from pkg import ...`); static green is necessary, not sufficient.
7. **Generated surfaces** — regenerate + prove idempotence (golden diff) if touched.
8. **Sprint closure** — increment boundary only: residue set EMPTY + behavior runs on the integration lane via its real surface (`sprint-closure`, UNIVERSAL_CORE Law 29).

## Report

Per phase: command, cwd, exit code, decisive output, covered scope; exact blocker for anything not verified. Never bypass a red gate or narrow the claim to hide a defect — fix the canonical owner and re-run with current evidence.
