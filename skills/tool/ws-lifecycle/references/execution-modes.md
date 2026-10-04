# Workspace execution modes

Choose exactly one mode before effects.

## Delegated

Route the tracked item through the active city's declared surface, for example
`gc sling <target> <bead> --on <formula>`. The selected formula and runtime own
placement and session startup. The coordinator does not pre-create a Git worktree and
must not describe a successful dispatch as work it executed. Before dispatch, read the
formula's provisioning base: the `gascity` `do-work` step cuts its worktree from
`origin/HEAD`, which must name the rig's integration lane (`rules/coordination/gascity.md`).

## Explicitly self-owned

When the operator explicitly retains execution, do not invoke `gc sling` or claim a Gas
City session. The repository owns its Git lane: fetch the declared integration ref,
create an isolated tracked worktree with
`git worktree add --track -b <branch> <path> origin/<integration>`, and record the exact
`work_dir`, branch, base, and initial SHA in the repository's selected tracker. Then use
the repository's current checkpoint and landing surface. Integrate base movement with
`git merge --no-ff`, never `git rebase` or `git pull --rebase`. Retire the worktree only
after `git fetch origin <integration>` refreshes the tracking ref and
`git merge-base --is-ancestor <branch> origin/<integration>` then succeeds.

`make work` owns neither mode. Never dispatch and also create a self-owned lane, or use
a local worktree as evidence that Gas City dispatched, placed, or ran an agent. Without
explicit self-owned authority, the active or suspended Gas City boundary remains
unchanged.
