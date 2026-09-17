# Bounded dispatch procedure

## Admit concurrency

Use one owner by default. Admit multiple agents only when the current operator or
approved plan authorizes concurrency and parallel work has a material latency or
evidence benefit. Before any dispatch, prove all of the following for every lane:

- a distinct objective and canonical owner;
- disjoint writable files, generated families, indexes, and external state;
- explicit inputs, exclusions, observable acceptance criteria, and native gates;
- no unresolved architecture, security, production, destructive, or public-
  contract decision; and
- a coordinator-owned integration dependency and final combined validation.

Distinct read-only research questions may run concurrently. A shared Git index,
file, generated family, migration cutover, release queue, environment, cluster, or
other mutable owner is serialized. Split no atomic old-to-new cutover between
writers.

## Construct the handoffs

Resolve the active roster at dispatch time and rank only material trigger overlap.
Each handoff states the objective, owner, readable and writable scope, exclusions,
current branch and repository context, accepted concurrent work, prohibited
behavior, required evidence, focused gates, integration gates, and stop conditions.

Include the allowed lane command forms and selected gates in the handoff body.
The worker runs plain `make <verb>` and `git <verb>` from its own session
worktree, `direnv exec <dir> bd <verb>` for bd, and `bun run --cwd` for package
scripts; worktree isolation refuses `git -C` and `env -C … make` against another
path. Define blocked behavior as
reporting the exact denial and options after 15 minutes with no written change
or green gate, never silently idling, switching lane, editing an occupied
checkout, or retrying a red gate.

Require the worker to reread mutable owners before edits, preserve compatible
current work, fix defects forward, and return changed paths, exact commands, exit
codes, decisive output, limitations, and risk. A worker does not gain authority to
merge, promote, publish externally, mutate production, or expand scope unless the
operator contract explicitly grants it.

When orchestration or tracking is suspended, do not invoke it and do not invent a
replacement. Use only the active client's native collaboration channel and the
already authorized Git, PR, review, and CI surfaces.

## Integrate the result

Review returned evidence and the actual diff; a worker message is not proof.
Integrate prerequisites first, reread the current integration lane before every
handoff, and rerun affected gates in the combined state. Keep shared mutable work
serialized throughout integration. A failed lane remains failed, propagates its
causal evidence, and cannot be repaired around or described as partial success.
