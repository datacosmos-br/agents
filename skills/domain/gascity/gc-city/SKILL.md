---
name: gc-city
description: 'gas city lifecycle, city init, start stop, supervisor status'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:gc-city","domain:gas-city","effective:2026-08-30","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","route:agent","route:project","technology:gas-city","updates:manual","usage:on-demand"]'
---
## Verification (mandatory)

Before acting on any bead, run the four-source cross-check in
`rules/coordination/beads-verification.md` and attach its evidence.

# City Lifecycle

A city is a directory with `city.toml` and `.gc/` runtime state.

## Initialization

```
gc init [path]                         # Initialize here or at path
```

## Start and stop

```
gc start [path]                        # Start the city (here or at path)
gc supervisor run                      # Foreground supervisor
gc start --dry-run                     # Preview what would start
gc stop                                # Stop the city
gc restart                             # Stop then start
```

`gc init` and `gc start` register the city and reconcile immediately. Interactive sessions: `gc session new <template>`. One supervisor hosts one reconciliation runtime per city, lock-enforced. Tick timing and `[daemon]` keys: `references/reconciliation-timing.md`.

## Status

```
gc status                              # Overview; unit owner
gc session list                        # Session / agent status
gc rig status <name>                   # Rig status
```

## Suspending

```
gc suspend                             # Suspend the city
gc resume                              # Resume suspended city
```

## Configuration and events

```
gc config show                         # Show resolved configuration
gc config explain                      # Show config provenance
gc doctor                              # Health checks
gc events                              # Tail the event log
gc event emit <type> [data]            # Emit event
```

## Dashboard and packs

Dashboard: the gc-dashboard skill. Packs add `gc <pack> <command>` subcommands and doctor checks — `gc pack list`, `gc pack fetch`.
