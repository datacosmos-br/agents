# Workspace execution modes

Choose exactly one execution mode before effects. Execution versus delegation is
not an isolation choice; `rules/coordination/gascity.md` owns placement.

## Delegated

Route the tracked item through the active city's declared surface, for example
`gc sling <target> <bead> --on <formula>`. The selected formula and runtime own
placement and session startup. The coordinator does not pre-create a Git worktree and
must not describe a successful dispatch as work it executed. Before dispatch, read the
formula's provisioning base: the `gascity` `do-work` step cuts its worktree from
`origin/HEAD`, which must name the rig's integration lane (`rules/coordination/gascity.md`).

## Explicitly self-owned

When the operator explicitly retains execution, do not invoke `gc sling` or claim a Gas
City session. Continue in the current authorized checkout and branch; isolation
requires explicit selection by the current invocation, not self-execution. Record
the actual `work_dir`, branch, base, and initial SHA in the selected tracker. Use
the repository's checkpoint and landing surface; coordinate WIP and serialize shared
index mutations. Integrate base movement with `git merge --no-ff`, never rebase.
Retirement requires separate authority for an owned disposable isolated context,
the Git owner's preservation and runtime-reference proofs, a fresh
`git fetch origin <integration>` and successful
`git merge-base --is-ancestor <branch> origin/<integration>`. Never retire an adopted
primary, integration, shared or foreign context. `shared-venv-guard` owns the physical
runtime-root environment; none of these modes permits borrowing one.

`make work` owns neither mode. Never dispatch and also create a self-owned lane, or use
a local worktree as evidence that Gas City dispatched, placed, or ran an agent. Without
explicit self-owned authority, the active or suspended Gas City boundary remains
unchanged.
