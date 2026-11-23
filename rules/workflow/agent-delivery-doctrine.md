---
description: Every red is the agent's; integration tip, native verbs, finish the DONE cycle in runtime
metadata:
  aihub.tags: '["decision:ADR-0040","effective:2026-11-23","route:both"]'
---

# Agent delivery doctrine

Operator order, 2026-11-23, for every session, project and agent.

1. **Every red is yours.** A failing `make` verb, `gen`, hook, CI check or gate is a
   defect in the change you made. The environment, the host load and the supplier
   toolchain are never the cause, and there is no "pre-existing" exemption. Repair
   the cause at its owner before you write again: a tree whose `gen` does not pass
   is not committable.
2. **The integration tip is the only base.** Fetch it, `git merge --no-ff` it before
   you commit, and do it again before you finish. Revalidate on the integrated
   revision; a lane on a stale base is a red waiting to happen.
3. **Native verbs run the work.** `make setup|gen|fix|fmt|check|tests|build|deploy`
   and the project CLI own their steps. Never bypass one, never add a second path
   beside it, never hand-run what a verb owns, never `--no-verify`.
4. **No agent surface is touched by hand.** Agent configuration, hooks, MCP entries,
   skills and policy are published by AI Hub through its declarations. A manual edit
   or a manual agent command is a defect: change the declaration and run the verb.
5. **Runtime first, then the gates.** Make the delivered behavior work in runtime
   first; run `make fix`, `make fmt`, `make check` and `make tests` only after it
   works, never the other way round. Finish the DONE cycle: commit from a message
   file, push, keep the PR open on the exact head, pass the required integration CI,
   merge the PR into the integration branch, and prove the delivered behavior in
   runtime again on the integrated revision. No phase is done without its merged PR
   and its runtime proof.
6. **Adopt, never duplicate.** Another agent's work is taken with `git cherry-pick`
   from its branch. Never reset, stash, rebase, discard or force-push it, and never
   open a second lane for the same work.
7. **One owner per value, file and surface.** Read it at the owner, repair it at the
   owner. A copy is a defect, not a convenience.
