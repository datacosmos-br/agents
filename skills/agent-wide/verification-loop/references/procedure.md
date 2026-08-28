# Verification Loop

"Done" requires fresh, real, timestamped green — not a claim. Run the gate in
order; any later edit invalidates earlier evidence, so re-run after changes.

## Use for

- Before saying a task/slice is complete.
- Before staging, committing, or handing off a PR.

## Completion Gate

Stop on first red; fix at the owner.

1. **Env/bootstrap health** — the venv and toolchain resolve.
2. **Lint + format** — global (`make check` lint,format).
3. **Static analysis** — `pyrefly` (baseline).
4. **Types for changed scope** — `pyrefly` + `mypy` + `pyright` on every changed
   file AND affected consumers (`make check CHECK_GATES=... FILES=...`).
5. **Tests** — `make test` for changed behavior (unit + integration as relevant);
   0 failed / 0 errors; a test >10s is a defect to fix, not to wait on.
   Impact selection (testmon) is authoritative: a green selected run closes this
   phase. Do NOT re-run the full suite to "double-check" a green subset —
   that is the hand-repeat forbidden by `UNIVERSAL_CORE` Law 7. Full suite =
   CI or explicit operator request only.
6. **Real-artifact use** — import/run the actual surface (CLI, daemon, `from pkg
   import ...`); static green is necessary but not sufficient.
7. **Generated surfaces** — regenerate + prove idempotence (golden diff) if touched.
8. **Sprint/increment closure** — at an increment boundary only: residue set EMPTY
   (dead code, compat shims, un-rewired consumers/tests, open worktree/PR/Bead)
   and the behavior runs on the integration lane via its real surface.
   Procedure + binary checks: `verification/closure`. `UNIVERSAL_CORE` Law 29.

## Report

For each phase: command, working dir, exit code, decisive output, covered scope,
and the exact blocker for anything not verified.

## Critical rules

- Never bypass a red gate, fake a failure, or narrow the claim to hide a defect.
- Fix the canonical owner and root cause; then re-run — evidence must be current.
