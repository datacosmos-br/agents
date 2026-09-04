# An approved plan owns its topic

At plan start or update, reconcile every correlated Bead, owner, WIP, lane,
worktree and PR. Preserve and adopt useful work into the canonical lane; an
occupied lane is never a blocker. Destroy or revert nothing.

When required work has not reached the integration branch, adopt it into the
owned lane by reviewed non-FF merge or cherry-pick. Preserve attribution and
revalidate the integrated result.
