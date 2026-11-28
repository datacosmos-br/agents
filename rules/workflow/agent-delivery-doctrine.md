---
description: Every red is the agent's; integration tip, native verbs, finish the DONE cycle in runtime
metadata:
  aihub.tags: '["decision:ADR-0040","effective:2026-11-24","route:both"]'
---

# Agent delivery doctrine

Operator orders of 2026-11-23, 2026-11-24 and 2026-11-25, for every session, project and agent.

1. **Every red is yours.** A failing `make` verb, hook, CI check or gate is a defect in
   the change you made; there is no "pre-existing" exemption. Repair it at its owner
   before you write again: a tree whose `make check` does not pass is not committable. The
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

1. **Fetch and merge.** Work on a branch cut from the integration tip. `git fetch` the
   integration branch and `git merge --no-ff` it into the lane before any work and again
   before finishing. The integration branch only receives merges: one lane, one branch,
   one PR, and coordinate before touching another lane.
2. **Prepare the lane.** `make setup` provisions the lane. `make upg` is the only writer
   of versions and locks and always resolves the newest integrated tip; never edit
   `uv.lock`/`mise.lock` by hand — on a lock conflict take the integration side and let
   `make upg` re-resolve. `make mod` runs only when a structural rewrite is ordered.
3. **`make check` is the single gate** (ADR-0042, FLEXT ADR-037). Outside CI it first converges gen → fix → fmt to a fixed point (at most five passes), then runs the
   read-only gates; in CI (`GITHUB_ACTIONS`) it converges nothing and fails on any byte
   that would change. `gen`, `fix`, `fmt`, `lock` and `ci` are not public verbs. The
   commit hook runs `make check`; never add a setup row or use `--no-verify`. CI runs
   `make setup`, `make check` and the test verb. `check-full`/`tests-full` run only on
   the operator's order, never in a PR or CI.
4. **Validate the runtime.** When the slice ships runtime or artifacts, `make build` and
   prove the behavior at its real entry point, also through other sessions' logs. A slow
   or integration test red in a lane is expected where the lane differs from the
   integration tip; CI deselects it — never weaken the test or the lock to go green.
5. **Do not hand-run** a gate "just in case": `make check`, the hook and CI are that gate.
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
prohibited. Host load holds only the full forms (`check-full`, `tests-full`, `mod-full`),
which are diagnostics and never a PR or CI gate; every other verb runs at any load, and
their absence never blocks CI.
