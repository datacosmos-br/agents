---
description: Bead verification is critical and mandatory
capsule_summary: |
  Creating, updating or closing a bead requires four independent sources:
  registered state, git history on the integration lane, measured reality
  (command, cwd, exit code, decisive output) and current integrated code.

  The bead is the hypothesis and reality is the proof. Closing without all four
  is a violation. When they diverge, fix the bead, never reality; close a
  retired premise as obsolete with evidence rather than executing it.

  A tracker's default listing truncates. A truncated output is never evidence
  of a complete population; an inventory that authorizes a conclusion uses the
  explicit unbounded form, e.g. `bd list --all --limit 0`.
metadata:
  aihub.tags: '["decision:ADR-0007","effective:2026-09-10","route:both"]'
---

# Bead verification is critical and mandatory

At creation, update and close, every bead passes four independent sources:

1. **Registered state** — authorized documents, handoffs and receipts; correct
   contradictions at their ledger owner.
2. **Git history** — commits and merged PRs on the integration lane.
3. **Measured reality** — disk, processes and endpoints, with command, working
   directory, exit code and decisive output.
4. **Current-code intent** — integrated HEAD, never an older revision. Close a
   retired premise as obsolete with evidence; never execute it as written.

The bead is the hypothesis; reality is proof. Closing without four-source
evidence is a violation. Fix divergence in the bead, never in reality.

A tracker's default listing truncates. A truncated output is never evidence of
a complete population: any inventory that authorizes a conclusion — the full
open set, a closure claim, a dedup or reconciliation sweep — uses the explicit
unbounded form (for `bd`, `bd list --all --limit 0`, filtered by status) and
records the command it ran.

Each managed execution uses one HQ root and linked bead per rig, both carrying
four-source checkpoints. Instructions, tracker prime, and skills enforce this;
divergence, parallel roots, and mail ledgers fail.

Compose with `provenance before conclusion` (rule file).
