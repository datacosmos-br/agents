# Documented claim

The guide says: `orchestrator dispatch worker work-42`, then
`orchestrator finish` commits, pushes, and merges the change automatically.

## Canonical static owner

- `orchestrator dispatch <agent> <work>` dispatches work only.
- The repository owns branch, commit, push, review, and merge.
- `orchestrator finish` and `orchestrator commit` are not declared commands.
- Runtime inspection is suspended; only static owner comparison is allowed.
