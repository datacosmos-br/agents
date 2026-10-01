# Rules — conduta e execução (2026-09-27)

Source: session retro zcode. These rules exist because real failures happened
without them. A session that violates one is red regardless of work delivered.

## R-S1. Read before plan

Plan only after reading: repo docs/adr, docs/plans, the governing rules file,
and current bead states. If the contract doesn't exist for the domain, write
it first (that is also a deliverable).

## R-S2. One writer per lane

Before starting on a lane: verify no other writer has commits or in-flight
edits newer than yours. The fleet's lane cleaner removes worktrees that look
inactive — an agent working inside a swept worktree loses everything.

## R-S3. Validate before pushing

The PR goes up READY: gen×2 fixed point, check, mod, and the touched tests all
green on the lane head. CI confirms — it never discovers.

## R-S4. Every execution has a timeout

A gate or suite invocation carries its declared budget. Slowness is a defect
cured at the owner (profile the stage, fix the cache) — never accepted as
normal, never masked by a bigger ceiling without measured justification.

## R-S5. The runtime is the oracle

Tests are more breakable than the runtime. When they disagree, measure the
runtime through its public boundary (real processes, real endpoints) and fix
the side that violates the contract — decided by the contract text, never by
which side is louder.

## R-S6. Beads are claims, not diaries

Claim before the first effect; heartbeat inside the abandonment threshold of rule
`bead-branch-pr-cadence` §2; every red found gets
a bead in the same turn; closure carries four-source evidence. Evidence in
scattered tmp logs is not evidence.

## R-S7. Coordination is written, proven, and bound to ownership

gc-mail `[coord] <kind> <facts> (<alias>)` with delivery proof by read-back.
The bead named; the branch named; the PR named. Criticism of another session
cites facts and the violated rule. A duplicate effort found in the wild is
reported as a coordination defect — and the duplicate is retired by whoever
did not have the claim.

## R-S8. Respect other sessions' worktrees

Never touch another session's worktree, branch, or in-flight edits. If the
lane looks abandoned under rule `bead-branch-pr-cadence` §2, verify via beads and
gc-mail BEFORE acting. Ask the coordinator if unsure.
