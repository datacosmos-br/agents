# Correction Reconciliation

## Evidence record

Record these fields in the Bead:

```yaml
correction:
  prohibited: prior behavior stated concretely
  required: replacement behavior stated concretely
  authority: operator message and date
  scope: global, personal, project, or technology
  incident: failure or risk that caused the correction
owners:
  docs: canonical documents or none
  skills: canonical skills or none
  adrs: superseded and superseding IDs or none
  prime_memory: ledger, key, and exact content
opposition:
  before: files and passages contradicting the correction
  after: zero, or an exact unresolved conflict
proof:
  commands: command, cwd, exit, decisive output
```

## Contradiction audit

Search semantic opposites, not only exact wording. For a rule such as “never use
raw clone”, search for `git clone`, manual worktree creation, alternate checkout
roots, temporary staging, and examples that teach those paths.

Classify every match:

- owner to edit;
- historical evidence to preserve and mark superseded;
- generated consumer to regenerate;
- unrelated example with a documented reason to retain.

The audit fails if active guidance still recommends the prohibited behavior, if
the new rule exists only in a projection, or if `bd prime` does not show the
keyed memory after persistence.

## Checkpoint behavior

At every checkpoint, compare operator corrections since the prior checkpoint
against files changed since then. If a correction has not reached all owners,
pause feature work, reconcile it, validate, update the Bead, then resume the
original plan.
