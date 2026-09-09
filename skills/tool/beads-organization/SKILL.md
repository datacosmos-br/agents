---
name: beads-organization
description: 'beads organization, family adjudication, rehome, deduplication, hierarchy repair'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-organization","effective:2026-09-09","route:agent","subject:beads","usage:router"]'
---

# Beads Organization

Activate when organizing beads into families, adjudicating duplicates,
re-parenting hierarchy, closing resíduo, or aligning with an external tracker.

## Ruler (apply to EVERY bead before any mutation)

1. **Adjudicate per family and owner — NEVER per textual similarity.**
   `bd find-duplicates groups pairs like the market: two beads with modeled
   titles are often sibling steps of the same DAG, not duplicates. Prove the
   dispatch by PR/branch/owner/scope before deciding any.
2. **Re-read the bead before changing anything.**
   It is prohibited to change `status`, `issue_type` or `parent` without
   `bd show <id>`. Parent is initialized by the `parent` field of
   `bd list --json` — it diverges from the real one; the authority is the
   PARENT/CHILDREN section of `bd show` (children under `↳`).
3. **Three only permitted closures:**
   - `SUPERSEDED:` another bead/greater family absorbed the same scope;
   - `OBSOLETE:` the platform/PR/branch/scope disappeared (ex.: Gas City
     retired → close the board + children with evidence);
   - `DONE:` executed and proven (command, cwd, exit, final output).
   If the work is legitimate and has no duplicate → **do not close**; register
   the comment and keep it open.
4. **Zero closed parent with a pending child.** Before closing any parent:
   read ALL pending children (`↳ ○/●` in `bd show`), chase one by one, only
   then close the parent. Warning: a batch that closes an epic before the
   children is an invalid batch.
5. **Canonical dispatch:** a family is absorbed by the channel that matches
   the actual plan of the project (ADR/plan newest, e.g. ADR-0023). Older
   family is closed as REHOME after `bd update --parent` on every child that
   is **not** of the theme of the survivor goes to the true owner
   (one-owner-per-concept). Think-colections: split by topic before any
   re-parenting in blocks.

## Re-home procedure (anchoring family absorbed)

```bash
bd show <old-epic> | sed -n '/^CHILDREN/,/METADATA/p'   # authoritative children
bd update <child> --parent <canonical-epic>             # one by one, no batch
printf 'close <old-epic> REHOME: ...absorvida por <canonica>; N filhos lidos e re-homed' | bd batch
```

- `bd batch` accepts ONLY `close/update(status,priority,title,assignee)/
  create/dep add/dep remove`, max 20 operations per batch.
- `parent` and `issue_type` go only via `bd update --parent/--type`
  (individual); there is no batch support.

## Deduplication Gate (mandatory after each batch)

1. `bd find-duplicates --status open --limit 0 --json` — count the pairs.
2. For each pair: read both beads, group by family, decide
   `SUPERSEDED/OBSOLETE` (close, with reason) or `LEGITIMATE:`
   (comment on both, do NOT close).
3. Re-execute the gate after the batch. Goal: zero pairs not adjudicated.

## Graph hygiene (after every batch)

```bash
bd doctor --check=validate     # orphan deps -> bd dep remove
bd orphans                      # regressao: zero novos orfans crados pelo lote
bd status --json                # permute: open/in_progress/blocked
```

- An orphaned edge to other ledger (`gc-*` etc.) can be removed with
  `dep remove` — it does not resolve here.
- `--check=pollution` notifies closed historical records (a warning
  accounts registers already closed) — does not purge anything without
  the operator.
- `doctor` checks available: `artifacts|conventions|pollution|validate`
  (orphans/duplicates/conflicts are part of `validate`).

## Epic consolidation (kinds)

- `KEEP-LANE`: live epic, unique scope, own children — keep.
- `RETYPE`: leaf epic that is in practice a task/bug (children=0 or single
  delivery) → `bd update --type task` + comment `RETYPE:`.
- `REHOME`: old family absorbed by a new one → re-home children, close
  parent `REHOME:`.
- `CLOSE-SUPERSEDED`: parent without unique scope after all children
  resolved. Never `RETYPED` an epic with alive children.

## Limits and registry

- max 20 `bd batch` operations per batch; always re-executed the gate after.
- every mutation is used in the coordinator bead (progress, counts, evidence):
  `bd update <coord> --append-notes`.
- external exports untouched (`aihub-beads-*.json/csv`) — never commit nor
  delete.
- discriminative double-check: `bd status` uses derived blockers and diverges
  from raw inventory (`bd list --all --limit 0 --flat --skip-labels --json`);
  register both in the coordinator.

## Closure/External References

- `bd close --reason` pattern: prefix + explanation (see Ruler 3).
- The bead closed with open external ref (or the inverse) fails the next
  sync audit; check `bd doctor --check=conventions`.
- Exit condition of the session: inventories, doctor validate, duplicates
  and re-count registered in the coordinator bead.
