---
description: "Session startup is a mandatory census: fetch the integration tip, count open PRs, census worktrees and branches (stale = adopt), census beads (silent >1h = abandoned), and declare bead + branch + PR before the first effect."
capsule_summary: |
  Operator ruling 2026-09-27 (session gascity-23): every session opens with a
  measured census, not with code. Measured cost of skipping it: one full lane
  built on a stale tip while the sibling session landed the same work (flext
  infra, ~2-3h lost), and a second lane opened against a base that moved 5
  commits during implementation.
metadata:
  aihub.tags: '["effective:2026-09-27", "route:both", "source:session-gascity-23"]'
---

# Session startup census

## The census, in order, before the first effect

1. **Fetch the integration tip** and read its log — the tip moved while you
   were away, and sibling sessions land in bursts.
2. **List open PRs** on the repo and their head branches — a PR whose head is
   your target file set is someone else's active lane.
3. **Census worktrees and branches**: last-commit date, dirty state, merged
   into the integration branch? A branch with no activity beyond the
   abandonment threshold (30h for lanes/worktrees) is abandoned: diff it
   against the tip, port the useful delta into your lane, close the rest with
   recorded disposition, delete the residue with ancestry proof.
4. **Census beads**: every bead silent for more than 1 hour — claimed,
   deferred, or blocked included — is abandoned and up for adoption. Claim
   with `--force` when a stale lock blocks, and keep every touched bead on a
   one-hour keep-alive from that moment.
5. **Declare bead + branch + PR** to the coordinator (`gc mail`) and on the
   bead itself. The declaration is the lane's birth certificate: without it,
   the work is unowned and lost.

## During the session

- One heavy gate at a time (see coordination/heavy-gate-serialization).
- Bead keep-alive at every boundary: effect applied, gate passed, PR opened,
  merge landed, red attributed to a named owner.
- At the end of each phase: no inactive worktree of yours survives, your PRs
  are merged or explicitly parked with disposition, and the integration
  branch's CI is green before the next phase opens.
