# Beads Organization Procedure

## 1. Preflight

Identify the exact Beads store and its lifecycle owner. Resolve the repository's
configured integration branch rather than assuming a branch name. If Gas City
owns the store, inspect its current state without starting, replacing, or
repairing its Dolt service. Missing authority or a suspended runtime permits
inventory only, not mutation.

Define the requested statuses, explicit limit, exact IDs when supplied, output
location, and whether closed history is in scope. A complete inventory requires
an explicit `--limit 0`; bounded work should use a positive limit.

## 2. Read-Only Inventory

Preview CSV on stdout without creating a file:

```bash
skills/tool/beads-organization/scripts/reconcile-inventory.sh \
  --limit 20 --integration <integration-ref> --dry-run
```

Create a review artifact, selecting IDs with repeated or comma-separated forms:

```bash
skills/tool/beads-organization/scripts/reconcile-inventory.sh \
  --limit 20 --integration <integration-ref> \
  --beads <id-1>,<id-2> --beads <id-3> --output <review.csv>
```

The script obtains records only through `bd list`, rejects unknown selected IDs,
and embeds repository, integration SHA, and current `git worktree` evidence in
every row. It reports possible inconsistencies only. It does not call any Beads
write or sync command. The output is not a mutation plan until an authorized
reviewer explicitly records the intended change and evidence for each selected
bead.

## 3. Evidence Review

For every candidate, compare four independent sources:

- registered Beads state read immediately before the decision;
- Git history and reachability on the configured integration branch;
- measured runtime, owner, process, branch, and worktree reality;
- current integrated code and its public behavior.

Plans, session exports, ADRs, docs, PRs, old branches, and commit subjects provide
provenance but do not override current reality. For a weak commit subject, inspect
the unchanged SHA's diff and integration reachability, then record the affected
capability and observable behavior. Never rewrite published history for wording.

## 4. Adjudication

- Keep distinct workflow spec, logical-step, and iteration-control records when
  their metadata and dependencies prove separate executable roles.
- For a true duplicate, select one owner and close the absorbed record with a
  `SUPERSEDED:` reason naming the survivor and evidence.
- Use `OBSOLETE:` only when current code, platform, branch, or scope evidence
  proves the requested work no longer exists.
- Use `DONE:` only after integrated behavior and required gates prove completion.
- Re-parent open children before closing a parent. Use the installed `bd` command
  form documented for that store; do not infer parent state from CSV alone.
- Release a claim only after proving there is no live owner, process, branch, or
  worktree. A timestamp alone is insufficient.
- Keep bugs at root with `bugfix`; add `hotfix` only for P0/P1. Remove those
  labels from non-bugs and lower-priority bugs.

## 5. Reviewed Mutation Batch

No inventory row is executable by itself. Before each write, require reviewed
input that names the bead, exact intended field/dependency/closure change, and
current evidence. Re-read the bead through `bd`; if its state differs from the
reviewed input, stop without applying the stale decision.

Apply at most 20 reviewed operations. Preserve the first command failure and its
output. Do not retry a stale batch, normalize an error, or continue with later
rows. Record applied IDs, sources, operation count, and first failure on the
selected coordinator bead when tracker mutation is authorized.

## 6. Gates and Continuation

After each batch, re-read changed records and run the store's documented Beads
duplicate, graph/cycle, orphan, parent-state, and convention checks. A mechanical
duplicate match is unresolved until each pair is either corrected or explicitly
adjudicated from metadata.

Only a fully validated batch may proceed to an operator-authorized Beads or
external-tracker sync. Record the exact command, working directory, exit status,
and remote result. Restart from a fresh bounded inventory after sync. Exit only
when the requested population has no unreviewed candidate, graph defect, stale
claim, invalid deferred state, or tracker/integration divergence.
