---
name: plan-handoff
description: Start a file-owned execution handoff from plan files and measured current state, never a transcript.
argument-hint: "<plan directory containing 00-index.md>"
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-09-03","intent:inspection","risk:external","route:agent"]'
---

# Plan handoff

Treat `$ARGUMENTS` as one local plan directory. Require `00-index.md`; reject an
ambiguous, missing, symlinked, or transcript-only handoff before any effect.

1. Read `00-index.md` first, then the handoff file, context/evidence, bead
   reorganization, and the phase named as current. Never resume a source session or
   import its cursor as authority.
2. Run the plan's preflight commands exactly, read-only where it declares read-only.
   Record command, working directory, exit code, and decisive output. On divergence,
   investigate provenance, correct the plan at its owner, and preserve all dirty work.
3. Reconcile the next bead with the canonical tracker before claiming. If the tracker
   runtime is suspended, do not create a substitute; proceed only through separately
   authorized Git/PR/CI evidence and leave closure open.
4. Claim one concrete next bead and state the objective, owned paths, allowed worktree,
   gates, stop condition, and current integration lane before mutation.

Return the accepted/rejected handoff decision, the first claimed bead, measured
preflight deltas, and the exact next command. A failed gate, dirty unexplained work,
missing authority, or conflicting plan keeps the handoff unaccepted.
