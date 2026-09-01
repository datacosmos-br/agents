# Reconciliation timing

How often the controller converges a city, and which `[daemon]` keys govern it.

## The process

`gc supervisor run` is the canonical long-running process: one machine-wide
supervisor hosting one reconciliation runtime per registered city. `gc start`
registers the city with that supervisor and waits for it to become active.

At most one controller runs per city, enforced by a lock. A second one fails
immediately rather than racing — never work around this by starting another.

## Keys

```toml
[daemon]
patrol_interval  = "30s"   # reconciliation tick frequency
max_restarts     = 5       # crash-loop threshold (0 = unlimited)
restart_window   = "1h"    # sliding window for restart counting
shutdown_timeout = "5s"    # grace period before force-kill
wisp_gc_interval = "5m"    # disabled unless set together with wisp_ttl
wisp_ttl         = "24h"   # disabled unless set together with wisp_gc_interval
```

## What one tick does

Reload changed config → rebuild the desired agent set → reconcile sessions →
run wisp GC → dispatch due orders.

Timing consequences to reason with:

- Config edits are debounced 200ms and land on the **next** tick, so a change
  takes effect within roughly one `patrol_interval`. This is not a stall.
- Reconciliation is idempotent: a healthy session with a matching config hash is
  skipped. Repeated ticks do not cause churn.
- Wisp GC runs only when `wisp_gc_interval` **and** `wisp_ttl` are both set.
- Changing `workspace.name` is rejected on reload and requires a restart.
- A hung pool `scale_check` blocks the whole tick — there is no per-check
  timeout. Suspect it first when every session stops converging.

Shutdown interrupts all sessions, waits `shutdown_timeout`, then force-kills
survivors. A zero timeout skips the grace period entirely.

Session states, the drain handshake, pool capacity, and config drift: the
gc-agents skill, `references/lifecycle-reconciliation.md`.
