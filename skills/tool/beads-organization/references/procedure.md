# Beads Organization Procedure

## Orphan Verification Query

```bash
bd list --status open --json | jq '[.[] | select(.parent != null)] | group_by(.parent) | map({parent: .[0].parent, count: length})'
```

Cross-reference each parent ID against the open feature list; any parent not
in that list is an orphan requiring resolution. Re-parent with
`bd link <child> --type parent-child --target <new-parent>` or close with
`bd close <child> --reason "OBSOLETE: pai fechado, trabalho absorbed"`.

## Dedup Adjudication

The mechanical gate reports similarity, not semantics. Before closing a pair,
read both beads' metadata: a Gas City workflow legitimately holds a spec bead,
a logical step bead, and an iteration control bead for the same step
(`gc.spec_for`, `gc.logical_bead_id`, `gc.iteration`). Record the adjudication
as a comment on the surviving bead so the next gate run does not re-flag it.

## Creation Limit

Max 20 issues created per single command invocation. A larger batch requires
`--dry-run` first and explicit operator review of the preview output before
the write executes.

## Zero Residue

After any beads reorganization:

- No `/tmp` staging files remain.
- No ad-hoc scripts that bypass the `bd` CLI.
- No `__pycache__` or build artifacts in tracked directories.
- `git status --short` shows only the expected changes.
