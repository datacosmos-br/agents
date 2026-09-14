---
name: beads-orchestrator
description: 'beads orchestration, dependency governance, tracker ownership'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-orchestration","effective:2026-08-29","route:agent","subject:beads","usage:router"]'
---

# Beads Orchestrator

Activate only for an explicit semantic graph or ownership decision by the
designated tracker orchestrator. Implementation of an assigned slice belongs to
the worker role.

Resolve Available versus Explicitly suspended from the active repository
contract. During suspension, inspect supplied evidence only and produce a
read-only convergence plan. Never invoke or replace the tracker.

When available:

1. Read the graph revision, objective, evidence, dependencies, claims,
   integration, authority, and linked city-root/rig-local pairs. Search first:
   one objective has one shared root, never a per-agent replacement.
2. Classify each requested node from evidence. Staleness alone never abandons a
   claim; a foreign or ambiguous claim blocks mutation.
3. Require each executing rig to own a local bead linked by metadata to the
   shared root and child. The root owns coordination; the local bead owns
   repository evidence. Missing or divergent links fail before effects.
4. Derive one complete mutation set from the current graph. Re-read immediately
   before effects; any revision change invalidates the plan.
5. Apply the authorized set atomically through the canonical tracker owner and
   verify the resulting graph. Never hand-edit storage or use alternate routing,
   commands, providers, credentials, retries, partial re-parenting, or inferred
   closure.

A reconciliation of records created during suspension follows the same
revision, identity, atomicity, and verification rules. Historical text is input;
only the canonical tracker is output.

The first graph, authority, runtime, or persistence failure propagates unchanged
and leaves the prior graph authoritative. Remove partial local artifacts before
handoff.

## Orchestrator execution pattern (multi-repo lanes)

When coordinating an owned plan across repositories or submodules:

1. Bead first. Create/claim the coordinating bead before any file write, shell,
   or multi-step work (`bd create --title ... --label P0`, claim, link parent
   epics). Update it after every repo-state change, not only at the end.
2. Explore with parallel subagents, never serially: one read-only agent per
   repository/surface (root, fleet owner, each submodule, tracker state) with
   structured findings (branch, HEAD vs gitlink, dirty files, gates state, open
   PRs). The orchestrator decides; subagents never own lanes.
3. Derive the mutation order from dependency direction — fleet/template owner
   first, then consuming root, then submodules, root gitlink pointers last in a
   separate commit. A shared checkout's lane belongs to its existing owner
   branch (fix-forward, no parallel branch).
4. Record closure evidence from four independent sources per repository: exact
   command + exit + decisive output, merged PR SHA, CI run, and runtime proof
   of the delivered behavior. Close only with all four attached
   (`bd close <id> --force --reason`).
5. Keep one material-state section in the plan (branch, HEAD, dirty files,
   ahead/behind per repo) refreshed at every cutoff so a resumed session
   reconciles from evidence, not memory.
