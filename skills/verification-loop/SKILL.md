---
name: verification-loop
description: "Run at every completion boundary before claiming work done. USE FOR: continuous-green gating in order (env, lint, types, tests, real-artifact use), proving behavior on the integration lane, blocking evidence-less done claims. DO NOT USE FOR: increment/sprint closure accounting (sprint-closure); choosing make targets (make-check)."
license: MIT
metadata:
  bundle: verification
  scope: universal
---

# Verification Loop

"Done" requires fresh, real, timestamped green — not a claim. Run the gate in order; any later edit invalidates earlier evidence, so re-run after changes.

## Use for

- Before saying a task/slice is complete.
- Before staging, committing, or handing off (`gt done`).

## Completion Gate

Stop on first red; fix at the owner.

1. **Env/bootstrap health** — the venv and toolchain resolve.
2. **Lint + format + static analysis** — global gates via canonical Make verbs.
3. **Types for changed scope** — on every changed file AND affected consumers
   (`make check CHECK_GATES=... FILES=...`).
4. **Tests** — changed behavior; 0 failed / 0 errors; a test >10s is a defect.
   Impact selection (testmon) is authoritative: a green selected run closes
   this phase. Full suite = CI or explicit operator request only — re-running
   it to "double-check" a green subset is the forbidden hand-repeat (CORE Law 7).
5. **Real-artifact use** — import/run the actual surface (CLI, daemon, import);
   static green is necessary but not sufficient.
6. **Generated surfaces** — regenerate + prove idempotence if touched.
7. **Integration lane** — at merge time: behavior exercised at the merged SHA;
   worker `--pre-verified` only after rebase onto target with gates re-run.

## Report

Per phase: command, cwd, exit code, decisive output, covered scope, exact blocker for anything unverified.

## Critical rules

- Never bypass a red gate, fake a failure, or narrow the claim to hide a defect.
- Fix the canonical owner and root cause; then re-run — evidence must be current.
