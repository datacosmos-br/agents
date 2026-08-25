---
name: beads-worker
description: "Contract for implementing an assigned bead in a Gas Town lane. USE FOR: executing claimed work on your hook, atomic cycles with evidence, finishing via gt done merge queue. DO NOT USE FOR: dispatch or tracker semantics (beads-orchestrator); audits (governance-audit)."
license: MIT
metadata:
  bundle: beads
  scope: universal
---

# Beads Worker
## Session Start

```bash
gt prime          # role context
gt hook status    # durable assignment survives restarts
bd show <id>      # NOTES: continue from evidence
```

Only orch-assigned beads. Skip blocked (`bd blocked`). One bead, one path scope in the shared epic/feature lane.## During — Short Atomic Cycles

1. One bounded outcome per cycle: edit → gates → commit → evidence.
2. ZERO-RED: never commit/push with lint/type errors in scope — fix in-cycle.
3. Cooperative fix-forward: adopt concurrent useful hunks; never clobber other lanes.
4. Evidence: `bd update <id> --append-notes "<slice>: cmd/cwd/exit/decisive"`
5. Discovered work filed immediately (`-t discovered-from`); living docs in same change.

## Finish — Merge Queue

```bash
gt done --status COMPLETED   # submit branch → refinery merges
gt done --status ESCALATED   # blocker; skip MR
gt done --status DEFERRED    # paused; issue stays open
```

`--pre-verified` only after rebase onto target with gates re-run. Never open PRs by hand; Refinery owns merges. Report `READY_FOR_REVIEW`/`NEEDS_FIX`/`BLOCKED`: branch, SHA, diffstat, gates, risks.

Leave ZERO residue: superseded code deleted, consumers/tests rewired, no shim — else NOT `READY_FOR_REVIEW`. See `verification/closure`.

## Conflict Escalation

Foreign/blocked claim → stop, re-read, confirm with orch. Overlap → serialize via orch. Unresolvable → `gt escalate` with both states.

## Context Budget

Load: CORE + governance/rules + this + project AGENTS (+ domain law on marker).
