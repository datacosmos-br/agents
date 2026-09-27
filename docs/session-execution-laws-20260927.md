# Session execution laws (learned 2026-09-27, zcode fleet session)

Seven blocking laws distilled from the failures of this session. Each exists
because a real failure happened without it. A session that violates one is red,
regardless of the work delivered.

## 1. Read the bases before planning (no assumptions)

Plan only after reading: the repo's docs/adr + docs/plans, the governing rules
file, and the current bead states. Two plans in this session were rejected as
"weak, headless" because they were written before the contract and the rules
were read. If the contract does not exist for the domain, write it first (that
is also a deliverable).

## 2. One writer per lane (collision = loss)

Before starting on a lane: verify no other writer has commits or in-flight
edits newer than yours. The fleet's lane cleaner removes worktrees that look
inactive — an agent working inside a swept worktree loses everything. Commit
and push every green milestone; never leave work unpushed longer than ~15 min.

## 3. Validate before pushing

The PR goes up READY: gen×2 fixed point, check, mod, and the touched tests all
green on the lane head. CI confirms — it never discovers. A red PR is a
process failure, not a discovery step.

## 4. Every execution has a timeout

A gate or suite invocation carries its declared budget (120 s for full suites
in the ai-hub law). Slowness is a defect cured at the owner (profile the stage,
fix the cache, fix the discovery) — never accepted as normal, never masked by
a bigger ceiling without the owner's measured justification.

## 5. The runtime is the oracle (tests are witnesses)

Tests are more breakable than the runtime. When they disagree, measure the
runtime through its public boundary (real processes, real endpoints) and fix
the side that violates the contract — usually the test, sometimes the product,
decided by the contract text, never by which side is louder.

## 6. Beads are claims, not diaries

Claim before the first effect; heartbeat at least hourly (a bead >1 h without
update is abandoned and can be taken); every red found gets a bead in the same
turn; closure carries four-source evidence (state, git, measured reality,
integrated code). Evidence in logs scattered across tmp dirs is not evidence.

## 7. Coordination is written, proven, and bound to ownership

gc-mail `[coord] <kind> <facts> (<alias>)` with delivery proof by read-back;
the bead named; the branch named; the PR named. Criticism of another session
cites facts and the violated rule. A duplicate effort found in the wild is
reported as a coordination defect — and the duplicate is retired by whoever
did not have the claim.
