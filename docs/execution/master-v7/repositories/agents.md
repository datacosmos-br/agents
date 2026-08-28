# Agents repository runbook

## Repository contract

| Field | Value |
|---|---|
| Working source | Existing `/home/marlonsc/.agents` checkout |
| Integration branch | `dev` |
| Future canonical source | `/home/marlonsc/agents` after final physical cutover |
| Accepted migration baseline | 85 flat skills, one canonical command, flat agents |
| Current work-lane inventory | Strictly discovered skills, commands, agents, rules, and their owned evaluations; counts are runtime output |
| Remaining target | Complete provider/runtime proof and full landing cycle |
| External imports | Prohibited |
| Tracker/orchestration runtime | Suspended; no invocation or substitute |
| Maximum attainable state during suspension | `LANDED_VERIFIED` |

Re-inspect current source and authorized Git/PR state before implementation.
Counts are discovered facts and migration evidence, not quotas or permission to
ignore a new or unknown artifact.

## Mission

Make this repository the single physical owner of personal/project agent
capabilities, reusable project skills, explicit commands, composed rules,
provider-native adapters, semantic Waza evaluation, and deterministic physical
projections. Complete the current inventory before any foreign source is
considered.

## Open defects

- Complete native and live evidence for the v5 personal/project projection,
  lifecycle adapters, and fixed point remains part of the landing cycle.
- CI, MCP comparison, target selection, and remaining runtime foundations still
  require the complete Phase 4 proof.
- The old source root must eventually be removed without a symlink or dual read.

## Repository sequence

### A0 — Documentation gate

Use only the active master v7 package and accepted ADRs. Run document links,
Markdown, terminology, and contradiction checks. Do not move an artifact before
this package is coherent.

### A1 — Models and discovery

Implement typed source models and recursive path/tag discovery. Keep a temporary
flat-input reader only inside the atomic migration; it cannot become a fallback
after the move. Remove identity/category/destination registries and prove the
generated index/manifest fixed point.

### A2 — Skills and commands

Perform the exact 85-to-76 skill migration and one-to-seven command migration.
Apply renames, removals, consumer rewiring, description/tag normalization, Waza
scenarios, BPE counting, and contradiction cleanup together. Add no capability
from outside this repository.

### A3 — Agents, rules, and adapters

Classify agents by distribution and semantic tags, consolidate only proven
duplicates, compose universal rules once, and render each artifact through its
provider-native adapter. Fail explicitly on unsupported combinations and
ownership conflicts.

### A4 — Runtime foundations

Fix all accepted review defects, exterminate keyring and its complete consumer
graph, require credentials directly from the process environment, and complete
storage/security contracts. Validate the optionless fail-loud
CLI/process/shell/projection runtime before complete gates. Do not use a live
model to make offline/unit/integration gates pass.

### A5 — Projection, model, and landing

Prove personal and isolated-project fixed points, run complete offline gates,
then use exact `aihub-primary` for the live gate. Complete authorized review and
merge-commit landing. The physical move to `~/agents` belongs to a separately
approved future increment and is prohibited here.

## Required repository gates

The complete accepted gate set is listed in
[Validation and landing](../06-validation-and-landing.md). Runtime evidence uses
the public `agentsctl` verbs; Make composes development gates only. At minimum,
the final evidence covers:

- document links and contradictions;
- recursive schema/discovery validation;
- every skill, command, agent, and rule semantic suite;
- BPE budgets and forbidden-update behavior;
- provider rendering and two-run projection fixed point;
- temp concurrency, signal, preservation, and shell parity;
- MCP generated/live drift;
- deterministic security manifest inventory and scanners;
- CI trigger/path coverage;
- exact-model live Waza after offline gates;
- post-merge runtime on `dev`;
- absence of current-increment superseded owners and consumer health.

## Session boundary

Do not operate another repository, destination home, Git branch, PR, or runtime
without the authority required by the current phase. Foreign provider files are
read-only evidence until the ownership manifest proves this repository created
them. A new session follows [Session protocol](../07-session-protocol.md) and
derives current state rather than copying stale command output into this runbook.
