---
description: Triage a daemon/binary publication chain failure with version-skew and runtime proof
metadata:
  aihub.tags: '["effective:2026-09-11","route:personal"]'
---

# runtime-skew-triage

Diagnose a publication-chain failure between a config publisher and its
long-running binary (e.g. CCS → CLIProxy, ai-hub daemon → CCS dashboard).

Load the skill `runtime-skew-triage` (agent-wide/verification) and execute its
six-step sequence. Non-negotiables:

- Prove the version pair (binary provenance + publisher source AND dist
  constant) before any redeploy or fix.
- Runtime proof = port listening + real endpoint response; never `is-active`.
- Map every assert of the chain (owner + failure class) before the first fix;
  predict where the symptom will displace.
- Quarantine orphaned transaction state with provenance suffix; file the typed
  rejection at the store owner.
- Fix at the owner, fix-forward; record exact commands, exit codes, and assert
  map status on the owning bead.

Reference case: `.kilo/plans/2026-09-11-status-review-plan.md` (ai-hub model
pipeline, 2026-09-11) and beads `aihub-37x3e`, `aihub-6k1.9`.
