---
name: beads-orchestrator
description: 'beads orchestration, dependency governance, tracker ownership'
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:beads-orchestration","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:beads","updates:manual","usage:router"]'
---

# Beads Orchestrator

Activate only for an explicit semantic graph or ownership decision by the
designated tracker orchestrator. Implementation of an assigned slice belongs to
the worker role.

Resolve Available versus Explicitly suspended from the active repository
contract. During suspension, inspect supplied evidence only and produce a
read-only convergence plan. Never invoke or replace the tracker.

When available:

1. Read the current graph revision, objectives, acceptance evidence,
   dependencies, claims, integration state, and actor authority.
2. Classify each requested node from evidence. Staleness alone never abandons a
   claim; a foreign or ambiguous claim blocks mutation.
3. Derive one complete mutation set from the current graph. Re-read immediately
   before effects; any revision change invalidates the plan.
4. Apply the authorized set atomically through the canonical tracker owner and
   verify the resulting graph. Never hand-edit storage or use alternate routing,
   commands, providers, credentials, retries, partial re-parenting, or inferred
   closure.

A reconciliation of records created during suspension follows the same
revision, identity, atomicity, and verification rules. Historical text is input;
only the canonical tracker is output.

The first graph, authority, runtime, or persistence failure propagates unchanged
and leaves the prior graph authoritative. Remove partial local artifacts before
handoff.
