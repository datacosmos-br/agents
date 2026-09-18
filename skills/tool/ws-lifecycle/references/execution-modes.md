# Workspace execution modes

Choose exactly one mode before effects.

## Delegated

Route the tracked item through the active city's declared surface, for example
`gc sling <target> <bead> --on <formula>`. The selected formula and runtime own
placement and session startup. The coordinator does not pre-create a Git worktree and
must not describe a successful dispatch as work it executed.

## Explicitly self-owned

When the operator explicitly retains execution, do not invoke `gc sling` or claim a Gas
City session. The repository owns its Git lane: fetch the declared integration ref,
create an isolated tracked worktree with
`git worktree add --track -b <branch> <path> origin/<integration>`, and record the exact
`work_dir`, branch, base, and initial SHA in the repository's selected tracker. Then use
the repository's current checkpoint and landing surface.

`make work` owns neither mode. Never dispatch and also create a self-owned lane, or use
a local worktree as evidence that Gas City dispatched, placed, or ran an agent. Without
explicit self-owned authority, the active or suspended Gas City boundary remains
unchanged.
