# Inviolable gate detail

## Execution extras

- Honor project serialization locks (Helm, package managers).
- `examples/`, `scripts/`, `tests/` share `src/` gates; exclusions explicit + Bead-tracked.
- Tree-mutating tests only on isolated fixtures.
- Pre-commit: `git diff --cached --stat` — intended paths only; `git restore --staged` surprises.
- No `git amend` for mistakes — new corrective commit.
- No impl on shared main/integration checkout except documented legacy baseline.

## Incident-derived hard rules

Each rule exists because the failure ALREADY happened. Violating one repeats a known outage.

- **Remote is ground truth** (2026-07-25): diagnose against the reference remote branch, never a
  local venv/editable/worktree state. A root-cause conclusion drawn on unverified local ground is
  void. Prove what is installed matches the reference branch before concluding.
- **Never mutate the shared venv from a lane** (2 outages in one night): `uv sync`/`uv pip`/
  `pip install`/`make setup` from a lane flips the shared editable `.pth` and breaks main and every
  other lane. Only the main checkout may mutate it; in a lane call the primary interpreter directly.
- **No temporary fix, ever** (2026-07-25, after recurrence): adjusting a surface "just to make it
  pass" is forbidden. The fix must make the canonical mechanism be used, be built correctly, and
  serve every situation (root, project, worktree, standalone, CI) — not only the case at hand.
  Workaround, shim, fallback, bypass, allowlist, exclude, xfail and suppression are never a delivery.
- **A missing tool is RED, never green**: absent binary, missing config, empty report or skipped scan
  must FAIL LOUD. Converting "tool not found"/"no config" into exit 0 is a fabricated green (P0).

## Complete refactor

Build complete typed/generated base first. Inventory with structural search + blast-radius tools. Same cycle migrate all consumers/projections; delete superseded. Real consumer before tests; regenerate via owner; prove idempotence.

## Green checkpoint extras

Prerelease/tag via project release automation only. Formal `main`/production needs operator approval + artifact verify. Smallest valid version bump; release verb owns bump/tag. Absorb stale-lane value before supersede.

## Workspace/test extras

Beads on detected workspace roots (or typed independent overlay). One conform/owner for generated root baseline. Stale assertion / live-env / isolation break = test defect. Behavior fail = code defect.

## Continuous-green / checkpoint / workspace / evidence / session

- Real consumer defines behavior; tests confirm; gates green; clean push; report artifacts. Procedure: `verification/loop`.
- Stage → gates → commit → FF push. Workers never promote `main`. Skills = real files.
- Typed inventory+Git. Tests ≠ SSOT; fixture-isolated. Config tests use SSOT (`UNIVERSAL_CORE` P0).
- Evidence = command/cwd/exit/output/scope/blocker. Orch validates; closes after integration+rollout.
- Heartbeats never stop work. Unowned WIP = stall. Loop until Beads clear.
