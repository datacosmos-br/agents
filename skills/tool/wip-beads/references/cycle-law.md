# Continuous bead governance cycle — law and closure

## Governance law (from plans 1788975913248, 1788980150347)

1. **Close only with 3 legal reasons**: `SUPERSEDED` (canonical owner named absorbs),
   `OBSOLETE` (scope/explicit disappeared with proof), `DONE` (cmd/cwd/exit/output).
   `LEGITIMATE` = comment both, DO NOT close.
2. **Zero parent closed with child pending** — check `↳` in `bd show` parent before
   close; re-home child by child (`bd update <child> --parent <owner>`), no batch.
3. **One canonical survivor per family** — defined by newest plan (ADR/§0.4/§0.7).
   Others close with survivor name in `--reason`.
4. **Cap 20 closes per batch** + validation gates.
5. **Never mutate active third-party lanes** (from §0.7 + claims ≤24h).
6. **Workspace evidence first** — root+submodules+worktrees before any status write.
7. **Subagent batch protocol**: coordinator generates CSV → splits via `--limits` →
   subagents dry-run per batch → coordinator reviews → `--apply` → evidence note per
   bead.

## Performance law (SSOT fetch)

One ledger fetch per mode, not per bead: load a single
`bd list --all --flat --limit 0 --json` snapshot at mode start and index it by id.
Per-bead `bd show` is a fallback only for ids missing from the snapshot. Re-fetch the
snapshot between modes, never reuse stale. Measured on a 102-bead ledger: one `bd show`
≈ 3.5s, so per-bead fetches cost ~6min per mode while a single snapshot runs the same
mode in ~20s.

## Evidence format (bd note)

```text
WORKSPACE SYNC <ISO8601> (wip-beads.sh <mode> [apply|dry]): <what changed>
beads=<n> batches=<n> apply=<0|1>
```

Co-verified with `bd show <id>` output when disputed. The note is the audit trail:
months later, "why does this bead have no parent?" is answered by this line plus the
classify dry-run log, not by memory.

## Completion criteria

- `bd doctor --check=validate` = 0 errors AND 0 warnings
- `bd find-duplicates` = zero unadjudicated pairs
- `bd orphans` = zero new orphans (each retained flag justified on the coordinator bead)
- Non-closed count ≤ 20% of baseline OR justified retention per family recorded
- All decisions documented on coordinator bead + snapshot saved

A cycle that ends with any gate red is NOT done — it is a documented handoff with the
failure named, owned, and queued.

(End of file)
