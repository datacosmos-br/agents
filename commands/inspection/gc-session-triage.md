---
name: gc-session-triage
description: Diagnose a Gas City session that will not start, stop, or drain, with evidence.
argument-hint: "<session id or alias, optionally the city path>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-30","intent:inspection","risk:external","route:agent"]'
---

# Gas City session triage

Treat `$ARGUMENTS` as one session ID or alias plus an optional city path.
Require the target and reject an ambiguous or missing one before any command.
Resolve the city's activation state from its own authority first, per
`rules/coordination/gascity.md`; while it declares suspension, restrict this
command to reading configuration and stop before any effect.

This is a read-only diagnosis. It never starts, stops, drains, kills, or resets a
session. Load the gc-agents skill reference
`references/lifecycle-reconciliation.md` for the state and handshake contract
before interpreting anything.

1. Establish ground truth in this order: `gc session list --json` for the bead
   state, then `gc status` for the controller, then `gc session peek` for what
   the process is actually doing. State reported by one source alone is a
   hypothesis, not a finding.
2. Classify the session's reported state and whether it occupies pool capacity.
   `creating` and `quarantined` occupy capacity; `archived`, `drained`,
   `asleep`, and `suspended` do not. A pool that will not grow while looking
   idle is usually held by `creating` or `quarantined` occupancy.
3. Separate *not desired* from *cannot start*. Check effective suspension
   through `workspace.suspended`, the rig, and the agent — never by looking for
   a `session.suspended` event, which has no production emitter. Check
   quarantine through crash-tracker state for the same reason.
4. When the session ignores a drain, report which metadata is actually set
   (`GC_DRAIN`, `GC_DRAIN_ACK`, `GC_RESTART_REQUESTED`, `held_until`) and
   whether the agent ever calls `gc runtime drain-check`. An agent that never
   polls cannot observe a drain, and `drain-ack` is what makes the stop
   immediate rather than next-tick.
5. When the session restarts repeatedly, distinguish the three running-state
   causes in their evaluation order — restart requested, idle timeout, config
   drift — and report which one fired. Do not attribute a restart to drift
   without the differing hash.
6. Before calling a drift finding real, confirm the stored hash carries the
   current fingerprint version prefix. A missing or older prefix is a silent
   rebaseline after a binary upgrade, not operator-intent drift, and must not be
   reported as an incident.
7. When reconciliation appears frozen for every session, suspect a hung
   `scale_check`: pool checks have no per-check timeout and block the whole
   tick. Report the offending agent's check command.
8. When a session's process keeps restarting or will not stop, resolve process
   ownership before touching the pid: `systemctl --user list-units 'gascity*'
   'ai-hub*'` for the owning unit's own state, then `journalctl --user -u
   <unit>` for its causal history, both before any `pgrep`. Distinguish a
   unit crash-loop (the unit exists and is restarting under its own policy —
   stop it only with `systemctl --user`, never by signal) from an orphan pid
   (`pgrep` finds a matching process with no owning unit — the only process
   eligible for a direct signal, per `rules/runtime/causal-subprocess.md`).

Return the session identity, its state and capacity occupancy, the single most
probable cause with the command, working directory, exit code, and decisive
output that proves it, and the specific remediation command left for the
operator to run. When the evidence does not converge on one cause, say so and
report the candidates — never present the most convenient one as established.
