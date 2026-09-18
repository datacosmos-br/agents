---
description: Partition every modified file as owned or foreign before staging
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# Owned or foreign: no dirty file is ever silent

Shared checkouts with active parallel lanes mean every working tree may hold changes you
do not own. `git add -A` in such a checkout once staged twelve foreign files under a
scoped commit and nearly absorbed another lane's WIP.

- Before any commit, run `git status --short` and partition every modified file:
  **owned** (this task's change) or **foreign** (another lane's work).
- Stage owned paths explicitly by path (`git add path1 path2`); never `git add -A` or
  `git add .` in a shared checkout.
- Foreign files are never restored, reset, or committed by the wrong lane: preserve
  them, and document the partition (paths + why foreign) in the tracker note for the
  checkpoint.
- If a foreign change blocks a required gate, escalate the blocker to the file's owner
  lane; do not adopt, absorb, or normalize it.
- Generated projections changed by a regen run with owned config changes are owned as a
  unit (config + regenerated projections in the same commit).

See also: `destructive-git-guard.md` (rule file), `fix-forward` skills.
