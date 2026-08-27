---
name: gastown-workspace-lifecycle
description: gastown, workspace, lifecycle, enforce, canonical, gas, town, placement, new, repositories
---

# Gas Town Workspace Lifecycle

Use this skill before cloning a project, creating a worktree, or choosing where
long-lived repository work should run.

## Routing

1. Inspect `gt rig list` to determine whether the repository is registered.
2. If it is new, run `gt rig add <rig> <git-url>` from the town root.
3. For persistent human or operator work, run
   `gt crew add <name> --rig <rig>`.
4. For a tracked agent task, claim the Bead and run
   `gt sling <bead-id> <rig>`.
5. Work only in the checkout Gas Town created.

Do not run raw `git clone` for a project already managed by the town. Do not
create manual worktrees alongside a rig. Do not adopt `/tmp`, a cache directory,
or an unregistered loose checkout as a project workspace.

## Storage Law

Clone staging, snapshots, checkpoints, build trees, and reports must stay on a
capacity-checked destination filesystem and have deterministic cleanup. The
system `/tmp` may hold small operating-system sockets and genuinely ephemeral
files; it must never hold a project clone, database copy, persistent cache, or
multi-gigabyte build workspace.

## Proof

Before reporting success, show the registered rig, the crew or polecat path,
and a clean `make temp` audit from the canonical agents authority.
