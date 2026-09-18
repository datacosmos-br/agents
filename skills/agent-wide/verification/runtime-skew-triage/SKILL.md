---
name: runtime-skew-triage
description:
  "binary/publisher version-skew triage, systemd runtime proof, cas race diagnosis"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","usage:router"]'
  version: 1.0.0
---

# Runtime Skew Triage

Use when a daemon that publishes configuration to a long-running binary fails after a
redeploy, upgrade, or restart — 4xx/5xx on publication, CAS conflicts, or "active but
dead" services. Distilled from the ai-hub model pipeline outage chain of 2026-09-11
(dc8→dc9 skew, stale intent, CAS active-flip, credential-refs race).

## When this applies

- Publisher and binary disagree on a schema/version constant (`v2 is required`,
  `unsupported schema-version`, digest mismatch).
- A service reports active but its port is closed or endpoint 5xx.
- A compare-and-swap stage rejects facts that the publisher itself mutated mid-cycle
  (probes, health checks).
- A persisted transaction/intent file from a previous binary era poisons every read
  until manually removed.

## Sequence (each step is evidence, not conjecture)

1. **Prove the pair.** Binary `--version` + embedded schema strings; publisher source
   constant AND deployed dist constant. Skew found → reconcile before any other
   hypothesis (rule: `runtime-version-skew.md`).
2. **Prove runtime, not unit state.** Port listening + one real endpoint call. An
   `active (exited)` unit is bookkeeping, not proof (rule:
   `runtime-proof-and-contract-first.md`).
3. **Map the full assert chain** of the publication path (identity → CAS subset →
   generation → parse → schema → credential subset → readback) with owner and failure
   class per assert. Predict where the current fix will displace the symptom.
4. **Quarantine, never delete, orphaned transaction state.** Move the stale artifact
   aside with a suffix naming the dead provenance (`intent-v3.json.stale-dc8-<date>`)
   and file the typed-rejection defect at the transaction-store owner.
5. **Fix at the owner, fix-forward.** Volatile fact classes (health, quota, suspension,
   credential-derived actives) belong in the CAS volatile set, not in snapshot freezing;
   the race root cause is fetch→publish non-atomicity, tracked separately.
6. **Close with bead evidence**: exact commands, exit codes, and the chain map updated
   with which assert now fails (or none).

## Anti-patterns (all measured 2026-09-11)

- Redeploying dist from source without re-proving binary compatibility.
- Trusting `systemctl is-active` twice before checking the port.
- Whole-blob diffing when a field-level diff isolates the cause in one read.
- Daemon retry loops to absorb a race the publisher should fix in-cycle.
