name: gc-city
description: 'gas city lifecycle, city init, start stop, supervisor status'
allowed-tools: Bash(gc *)
metadata:
  aihub.tags: '["activation:opt-in", "detect:opt-in:gc-city", "domain:gas-city", "policy:atomic-effects", "policy:causal-subprocess", "policy:fail-loud", "policy:no-fallback", "policy:preflight-before-effects", "policy:strict-execution", "provenance:agents-owned", "route:agent", "technology:gas-city", "updates:manual", "usage:on-demand"]'
---
## Verification (mandatory)

Before acting on any bead, run the four-source cross-check defined in
`rules/coordination/beads-verification.md` (project law): registered manual
ledgers, git history, measured reality, and the intent of the most recent
code. Declare the check and attach evidence — command, working directory,
exit code, decisive output — before closing. A bead whose premise the
current code retired is closed obsolete with evidence, never executed as
written.



# City Lifecycle

A city is a directory containing `city.toml` and `.gc/` runtime state.

## Initialization

```
gc init                                # Initialize city in current directory
gc init <path>                         # Initialize city at path
```

## Starting and stopping

```
gc start                               # Start city under the supervisor
gc start <path>                        # Start city at path under the supervisor
gc supervisor run                      # Run the supervisor in the foreground
gc start --dry-run                     # Preview what would start
gc stop                                # Stop the current city
gc restart                             # Stop then start
```

`gc init` and `gc start` register the city with the machine supervisor, ensure it is running, and trigger an immediate reconcile. Interactive sessions are created separately with `gc session new <template>`.

## Status

```
gc status                              # City-wide overview
gc session list                        # Session / agent status
gc rig status <name>                   # Rig status
```

## Suspending

```
gc suspend                             # Suspend entire city
gc resume                              # Resume suspended city
```

## Configuration

```
gc config show                         # Show resolved configuration
gc config explain                      # Show config layering and provenance
gc doctor                              # Run health checks
```

## Events

```
gc events                              # Tail the event log
gc event emit <type> [data]            # Emit a custom event
```

## Dashboard

See the gc-dashboard skill for full dashboard reference.

## Packs

Packs extend Gas City with additional commands, prompts, formulas, and doctor checks. Pack commands appear as top-level `gc <pack> <command>` subcommands.

```
gc pack list                           # List installed packs
gc pack fetch                          # Fetch remote packs
```
