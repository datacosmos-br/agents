# Dispatching Work — Convoys and Orders

## Convoys (grouped work)

```
gc convoy create <name> <bead-ids...>                 # Group beads into a convoy
gc convoy create <name> --owned --target integration/<slug>  # Long-lived initiative convoy
gc convoy target <id> <branch>                        # Set/update convoy target branch
gc convoy list                                        # List active convoys
gc convoy status <id>                                 # Show convoy progress + metadata
gc convoy add <id> <bead-ids...>                      # Add beads to convoy
gc convoy close <id>                                  # Close convoy
gc convoy check                                       # MUTATING: scans ALL open convoys city-wide and auto-closes any where all children are resolved
gc convoy stranded                                    # Find convoys with no progress
gc convoy autoclose <id>                              # Internal: invoked by bd's on_close hook to auto-close a closed bead's completed convoys
```

Migration note:
- Existing epic beads are no longer first-class containers. Migrate open epics to convoys before relying on convoy-only tooling such as `gc convoy target`, `gc sling <convoy>`, or the legacy refinery convoy flow.

## Orders

```
gc order list                     # List order rules
gc order show <name>              # Show order definition
gc order run <name>               # Manually trigger an order
gc order check                    # Evaluate all orders' trigger conditions and show which are due
gc order history <name>           # Show order run history
```
