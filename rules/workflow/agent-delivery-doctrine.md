---
description: Every red is the agent's; integration tip, native verbs, finish the DONE cycle in runtime
metadata:
  aihub.tags: '["decision:ADR-0040","effective:2026-11-24","route:both"]'
---

# Agent delivery doctrine

Operator orders of 2026-11-23 and 2026-11-24 (decided 2026-11-25: the cycle of FLEXT
#2791 prevails), for every session, project and agent.

1. **Every red is yours.** A failing `make` verb, hook, CI check or gate is a defect in
   the change you made; there is no "pre-existing" exemption. Repair it at its owner
   before you write again: a tree whose `check` does not pass is not committable. The
   environment and upstream are never the suspect ([law 13](../law.md)).
2. **Native verbs run the work.** The project's declared Make verbs and CLI own their
   steps. Never bypass one, never add a second path beside it, never `--no-verify`, and
   never change a project rule or add a make verb without the operator's decision.
3. **No agent surface is touched by hand.** Agent configuration, hooks, MCP entries,
   skills and policy are published by AI Hub from its declarations; a manual edit or a
   manual agent command is a defect: change the declaration and run the verb.
4. **Adopt, never duplicate.** Another agent's work is taken with `git cherry-pick -x`
   from its branch. Never reset, stash, rebase, discard or force-push it, and never open
   a second lane for the same work.
5. **One owner per value, file and surface.** Read and repair it at the owner; a copy is
   a defect. A definition fix propagates atomically to every user, never through
   compatibility code.

## The delivery cycle

Strict and ordered; no skill, ADR, project instruction or memory may contradict it.

1. **Fetch and merge.** `git fetch` the integration branch and `git merge --no-ff` it
   into the lane before any work and again before finishing.
2. **Prepare the lane.** `make setup` provisions the lane. `make upg` is the only writer
   of versions and locks, always resolving the newest integrated tip; it runs before
   `check` whenever a dependency or pin changes. `make mod` runs a structural rewrite only
   when one is ordered. A repository whose Makefile predates #2791 runs its own declared
   verbs until it is regenerated.
3. **`make check` is the only gate.** In FLEXT-projected repositories (#2791) the public
   verbs are `setup`, `upg`, `mod`, `check`, `tests`, `tests-full`; `gen`, `fix`, `fmt`
   and `lock` are no longer public, and CI is detected inside the Makefile and runs
   `check` verify-only. Target, not yet true: the default `check`
   (`CHECK_PHASE=primary`) converges generation, repair and formatting to a fixed point;
   until flext-infra `feat/check-converges` lands, run `CHECK_PHASE=complete` via
   `check-full` once when generated files change. Repair the cause at its owner; never
   change the expected shape to pass.
4. **Validate the runtime.** Prove the delivered behavior at its real entry point from
   the lane, and through other sessions' logs where they exercise it.
5. **The project's test verb** (`make tests` in FLEXT projects) is the last step before
   the commit.
6. **Commit, push, PR, merge.** Commit only after the cycle is green, with explicit paths
   from a message file, push, open one PR on the exact head, pass the required
   integration CI, merge into the integration branch. A new change reopens the cycle at
   `make setup`.
7. **Deploy last**, from the integrated revision's published release, and prove the
   behavior again at its real entry point.
8. **Done** follows [law 10](../law.md): the agreed functionality merged at the
   integration tip, green CI and proven in runtime; docs and ADRs updated and the Bead
   closed with the evidence. Anything less is in progress and names the missing step.

**The gate queue.** A verb that admits itself to the host gate waits in its FIFO queue
and the session waits with it; bypassing, pre-empting, cancelling or enlarging it is
prohibited. Host load holds only the full forms (`check-full`, `tests-full`,
`mod-full`); every other verb runs at any load. The full forms run only with a stated
need, and their absence never blocks CI.
