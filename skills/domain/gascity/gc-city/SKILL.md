---
name: gc-city
description: 'gas city lifecycle, city init, start stop, supervisor status'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in", "detect:opt-in:gc-city", "domain:gas-city", "policy:atomic-effects", "policy:causal-subprocess", "policy:fail-loud", "policy:no-fallback", "policy:preflight-before-effects", "policy:strict-execution", "provenance:agents-owned", "route:agent", "technology:gas-city", "updates:manual", "usage:on-demand"]'
---
## Verification (mandatory)

Before acting on any bead, run the four-source cross-check in
`rules/coordination/beads-verification.md` and attach the evidence it
requires.

# City Lifecycle

A city is a directory with `city.toml` and `.gc/` runtime state.

## Initialization

```
gc init                                # Initialize here
gc init <path>                         # Initialize at path
```

## Start and stop

```
gc start                               # Start the city
gc start <path>                        # Start at path
gc supervisor run                      # Foreground supervisor
gc start --dry-run                     # Preview what would start
gc stop                                # Stop the city
gc restart                             # Stop then start
```

`gc init` and `gc start` register the city with the supervisor, ensure it is running, and reconcile immediately. Interactive sessions: `gc session new <template>`.

## Status

```
gc status                              # City-wide overview
gc session list                        # Session / agent status
gc rig status <name>                   # Rig status
```

## Suspending

```
gc suspend                             # Suspend the city
gc resume                              # Resume suspended city
```

## Configuration

```
gc config show                         # Show resolved configuration
gc config explain                      # Show config provenance
gc doctor                              # Health checks
```

## Events

```
gc events                              # Tail the event log
gc event emit <type> [data]            # Emit a custom event
```

## Dashboard

Full reference: the gc-dashboard skill.

## Packs

Packs add `gc <pack> <command>` subcommands, prompts, formulas, and doctor checks.

```
gc pack list                           # List installed packs
gc pack fetch                          # Fetch remote packs
```
