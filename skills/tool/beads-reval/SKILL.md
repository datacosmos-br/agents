---
name: beads-reval
description: 'beads revalidation sweep, reval tag waves, csv tracker, code-reality validation'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-reval","effective:2026-09-10","route:agent","subject:beads","usage:router"]'
---

# beads-reval — Incremental bead revalidation sweep

Deep-revalidation program for a tracker ledger: every bead re-validated against
code reality, deduplicated, dependency-realigned, and closed or re-scoped, in
resumable waves marked by a sweep tag (e.g. `reval250909`).

## Operator laws learned in reval250909 (highest authority)

1. **Fix at the generator, never at one projection.** When a fleet-wide
   mechanism is defective, fix the mechanism's canonical owner so every
   consumer converges; committing corrected renders on one consumer makes the
   problem return. A defective mechanism is exterminated, never exempted.
2. **Exterminate means the whole family.** An operator-ordered extermination
   (e.g. `exclude-newer` and similar) removes the mechanism everywhere in one
   cutover: model fields, protocol members, writers, templates, SSOT config,
   overrides, tests — and the writer becomes an unconditional key remover so
   old projections converge (the `flext-gzfd2` pattern: a removed declaration
   exterminates the key everywhere; no orphan cap survives without an owner).
3. **Bugs and hotfixes live outside epics.** They stay at root with `bugfix`
   labels (`hotfix` only on P0/P1) and are revalidated in the same sweep.
4. **No rush; resume, don't rush to finish.** Sweeps are incremental across
   sessions; the CSV tracker and `bd remember` carry the resumption point.

## Wave plan (execute in order; tag everything touched)

- **W0 — Baseline**: `bd list --all --status open,in_progress,blocked,deferred
  --json > ~/[project]-reval.json`; convert to a CSV tracker with columns
  `id,title,status,priority,type,parent,labels,revalTAG,action,notes`. The CSV
  is the progress ledger; update it after every mutation.
- **W1 — Structural cleanup**: close formula/convoy/synthetic artifacts
  (OBSOLETE), true duplicates (SUPERSEDED with survivor named), fix stale
  blockers (a blocked bead whose only blocker is closed goes back to open).
- **W2 — Code-reality validation**: per bead, measure the named scope in the
  working tree (grep symbols, run the smallest real command, `gh run list` for
  CI claims). Record command + exit code + decisive output in the bead note
  with the sweep tag. False-premise beads close with evidence; valid beads get
  owner retargets (deleted crates, renamed layers).
- **W3 — Semantic dedup + dependencies**: fold same-deliverable pairs into the
  survivor (migrate unique content BEFORE closing), realign dependency edges
  from ADR evidence (port -> implementation, traversal -> graph), never trust
  mechanical similarity alone.
- **W4 — Implementation cycles**: the sweep's red bugs and blockers become
  bead-owned branches: bead first, change branch, native gates, push, PR,
  operator review, land on the integration branch, post-merge gates.

## Evidence and resumption

- Every closure: `DONE:` / `SUPERSEDED:` / `OBSOLETE:` with measured evidence.
- Every wave end: `bd remember "reval<TAG> ..."` with completed waves, open
  findings, and the next action; update the CSV `revalTAG` column (`DONE`,
  `DONE-2P`, `CLOSED`, `PR#N`, ...).
- Discriminate pre-existing red from caused-by-me: stash the change and rerun
  the failing test on the pristine base before claiming or absorbing blame.
- A swept bead that later changes state (PR merged, branch deleted upstream)
  gets a fresh measured note in the next pass; sweep state is never assumed.
