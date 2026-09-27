# ADR-0030 — Agent-session environment truth: the kernel owns process context, never inherited environment

**Status:** Accepted **Date:** 2026-09-27

## Context

Agent sessions on this host descend from a systemd user unit
(`gascity-supervisor.service`) that exports `INVOCATION_ID` and `SYSTEMD_EXEC_PID`
once; every agent shell, `make` invocation, and test process inherits those
variables while actually running in a session scope
(`user@1000.service/app.slice/app-<name>.scope`). Guards that classify "am I
inside a unit?" by the presence of an environment marker misclassify every
descendant. Measured consequence (ai-hub surfaced-inventory campaign,
2026-09-27): the credential projection guard refused `make install` from any
agent-spawned shell, and seven battery tests failed on fixtures that
deliberately simulate the operator's non-unit session. A session also lost
hours re-deriving context that an existing handoff had already documented, and
left its most valuable slice uncommitted until context exhaustion — both
recorded in the campaign retrospective
(ai-hub `.kilo/plans/2026-09-27-surfaced-inventory-runtime-recovery/00-index.md`,
`Retrospectiva crítica`).

## Decision

1. **Process context is read from the kernel, not the environment.** Whether a
   process belongs to a service unit is decided by its own cgroup
   (`/proc/self/cgroup`): scan segments right-to-left; the first segment ending
   in `.service` or `.scope` decides. `.scope` is a session; `.service` is a
   unit. `user@1000.service` appears in every user-session path and is the user
   manager, never the deciding unit. Inherited markers
   (`INVOCATION_ID`, `SYSTEMD_EXEC_PID`, `GC_SUPERVISOR_*`) are not evidence of
   anything about the current process.
2. **A guard that refuses by unit context refuses genuine unit processes and
   unreadable contexts only.** Unsetting the marker to pass a guard
   (`env -u INVOCATION_ID make install`) is a bypass and is prohibited; the
   guard is the defect and is cured at its owner.
3. **Tests own their context.** A test that needs a unit or session context
   injects it explicitly (fixture), never relying on the ambient environment
   being marker-free or marker-full.
4. **Sessions open with recovery, not rediscovery.** Every session working a
   governed project starts from the recorded surfaces (newest handoff, tracker
   prime, tracker context, coordinator inbox, worktree census, environment
   preflight) before any effect — encoded as the `session-recover` command and
   `rules/coordination/aihub-session-operating-rules.md`.
5. **A green slice is committed before any new exploration.** The commit is the
   context checkpoint; holding a finished slice uncommitted violates the
   landing cadence and risks losing the work to context exhaustion.

## Consequences

- The ai-hub credential guard gains a cgroup-leaf check (its decision record is
  ai-hub `docs/adr/0034-credential-projection-unit-guard.md`, renumbered from a
  colliding 0032); the canonical
  operator flow works from agent shells without bypasses.
- The battery becomes deterministic across execution contexts.
- The `session-recover` command and the operating rules carry the startup
  discipline; new sessions stop paying the rediscovery tax.
