# Session lifecycle and controller reconciliation

Operational contract for how the Gas City controller converges sessions, how a session
moves between states, and how pool capacity is bounded. Read this before diagnosing a
session that will not start, will not stop, restarts in a loop, or ignores a drain.

Product sources (Gas City repository, not this bundle):
`engdocs/architecture/{controller,health-patrol,session}.md`, `docs/reference/cli.md`,
`docs/reference/schema/city-schema.json`.

## 1. The reconciliation tick

The controller converges each city on `[daemon] patrol_interval` (default 30s) or on a
config change. Each tick: reload changed config (rebuilding all four trackers
atomically), rebuild the desired agent set, reconcile sessions, run wisp GC, dispatch
due orders. Tick timing and `[daemon]` keys: the gc-city skill,
`references/reconciliation-timing.md`.

Consequences to reason with here:

- Reconciliation is **idempotent** — a healthy session with a matching config hash is
  skipped with no side effects. Ticks are not a churn source.
- A hung `scale_check` **stalls the entire tick**: checks parallelize with each other,
  but the tick waits for all of them and there is no per-check timeout. Suspect this
  first when reconciliation looks frozen for every session.
- Config edits are debounced and land on the next tick.

## 2. Reconciliation state machine

| State              | Condition           | Action          |
| ------------------ | ------------------- | --------------- |
| Not alive          | should wake         | Start           |
| Healthy            | alive + desired     | Skip            |
| Orphan / suspended | not desired         | Drain or close  |
| Drifted            | config hash differs | Drain + restart |

For a session that **is** running, these are checked in order — the first match wins, so
an idle timeout preempts a drift repair:

1. **Restart requested** (`GC_RESTART_REQUESTED`) → stop + start.
2. **Idle timeout exceeded** → stop, emit `session.idle_killed`.
3. **Config drift** (stored hash ≠ current) → stop + start.

A session that is **not** running is subject to crash-loop quarantine: more than
`max_restarts` starts within `restart_window` and it is skipped silently until the
window ages out. Quarantine is in-memory, so a controller restart clears it and the
session is retried immediately.

Orphan cleanup handles city-prefixed sessions absent from the desired set: pool excess
is drained gracefully, suspended agents are drained or closed, true orphans are killed
immediately.

Diagnostic consequence: **`session.quarantined` and `session.suspended` are registered
event types with no production emitter.** Never diagnose quarantine or suspension by
subscribing to events — read the crash tracker state and the `workspace.suspended` / rig
/ agent chain instead.

## 3. Session states

Bead-backed session states, and whether they occupy pool capacity:

| State              | Meaning                                                                    | Occupies capacity |
| ------------------ | -------------------------------------------------------------------------- | ----------------- |
| `active` / `awake` | live runtime                                                               | yes               |
| `start-pending`    | identity reserved, no Start in flight                                      | yes               |
| `creating`         | Start in flight, not yet confirmed alive                                   | **yes**           |
| `asleep`           | dormant, no live runtime                                                   | no                |
| `suspended`        | paused, no runtime resources                                               | no                |
| `draining`         | graceful stop; routing label removed, no new work routed                   | yes               |
| `drained`          | drain acknowledged; stays dormant until an explicit compatible wake reason | no                |
| `quarantined`      | crash-loop threshold reached, blocked from waking                          | **yes**           |
| `failed-create`    | rollback wrote terminal metadata, bead close unfinished; replaceable       | no                |
| `archived`         | drain complete, retained for history                                       | **no**            |

`creating` and `quarantined` counting against capacity is the usual explanation for a
pool that refuses to grow while appearing idle.

## 4. Drain and restart handshake

Signals travel through session metadata; the controller acts on them at the next tick
unless the command pokes the socket.

| Command                             | Writes                 | Effect                                                                                       |
| ----------------------------------- | ---------------------- | -------------------------------------------------------------------------------------------- |
| `gc runtime drain <name>`           | `GC_DRAIN`             | asks the session to finish current work                                                      |
| `gc runtime drain-check [name]`     | —                      | **exit 0 = draining**, 1 = not                                                               |
| `gc runtime drain-ack [name]`       | `GC_DRAIN_ACK`         | pokes the controller socket so the stop happens immediately, not next tick                   |
| `gc runtime undrain <name>`         | clears both            | cancels the drain                                                                            |
| `gc runtime request-restart`        | `GC_RESTART_REQUESTED` | emits `session.draining`, then blocks idle while the controller kills the tree               |
| `gc runtime heartbeat [--duration]` | `held_until`           | suppresses idle-timeout **and** max-session-age; default 45m; auto-cleared by the reconciler |
| `gc hook --claim --drain-ack`       | `GC_DRAIN_ACK`         | acknowledges the drain when the claim finds no work                                          |

Agent-side pattern:

```bash
if gc runtime drain-check; then
  # finish the current unit of work, then:
  gc runtime drain-ack
fi
```

`request-restart` exits 0 when the controller kills the process tree, when the runtime
is already gone, or on SIGINT/SIGTERM. It exits **1 with a diagnostic** after
`max(5 × patrol_interval, 5min)`, capped at 30min — that exit code means _investigate
controller health_, never _retry the command_. If interrupted, the restart request stays
set for the next tick.

`heartbeat` does not suspend the session and does not change sleep intent. Use it around
long silent operations that would otherwise trip a false-alarm idle kill.

## 5. Pool capacity and routing

Agent-level keys. `min_active_sessions` / `max_active_sessions` are canonical and
replace `pool.min` / `pool.max`, which remain only as legacy override fields.

| Key                             | Meaning                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `min_active_sessions`           | minimum sessions kept alive; agent-level only; counts against rig and workspace caps                   |
| `max_active_sessions`           | agent cap; nil inherits rig → workspace → unlimited. A max of 0 means no session may claim routed work |
| `scale_check`                   | shell template reporting **new unassigned** session demand                                             |
| `drain_timeout`                 | wait for in-flight work during scale-down before force-kill; default 5m                                |
| `idle_timeout`                  | inactivity before kill + restart; empty disables it                                                    |
| `max_session_age` (+ `_jitter`) | preemptive restart of long-lived sessions; idle-gated; jitter desynchronizes a fleet                   |

**`scale_check` is additive under bead-backed reconciliation** — it reports only how
many _new generic_ sessions to start, because assigned work is resumed separately.
Legacy no-store evaluation still reads its output as the absolute desired count. Reading
it as a total is the common misconfiguration.

Routing is metadata-based, never direct dispatch: `gc sling` only stamps `gc.routed_to`
on the bead; the reconciler and `scale_check` decide when a session is created. The
three-tier `work_query` default and the claim-identity rules live in the gc-work skill,
`references/router-procedure.md`. One tier matters here: when the controller probes for
demand **without session context, only the routed-pool tier applies**, so a bead that is
assigned but never routed creates no pool demand.

## 6. Claim identity

Ownership reads and writes must use `${GC_ALIAS:-$GC_TEMPLATE}`; shared role queries use
bare `$GC_TEMPLATE`. Full tier-by-tier table and the duplicate-work failure it prevents:
the gc-work skill, `references/router-procedure.md`.

## 7. Config drift versus binary upgrade

Drift is detected by hashing config content, not timestamps. Stored hashes carry a `vN:`
prefix from the fingerprint version (currently `v5`).

Two cases are **silent rebaseline, not drift**: a stored hash with no prefix (written by
a pre-versioning binary), and a prefix that differs from the current version. Rebaseline
rewrites the stored hashes, keeps the session running, emits **no** draining event, and
logs one info line per session.

Operational consequence: after a `gc` upgrade, a one-time burst of rebaseline log lines
is expected and is not a fleet-wide drift incident. A real same-version hash change is
operator intent and does drain the session. Rotating an upstream credential moves no
fingerprint; switching the `upstream` **name** does.

## 8. Known limits

- Tracker state (crash history, idle timestamps, order dispatch) is in-memory and lost
  on controller restart. Intentional.
- No cascading restarts and no `depends_on` — only restart-the-dead-one.
- Idle detection does nothing on providers that do not report activity.
- Failed orders do not retry; the tracking bead only blocks re-fire inside the same
  cooldown window.
- Prompts render once at session start; a config change needs a restart.
