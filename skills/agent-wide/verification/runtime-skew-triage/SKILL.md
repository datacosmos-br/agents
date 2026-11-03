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
dead" services.

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
   hypothesis.
2. **Prove runtime, not unit state.** Port listening + one real endpoint call. An
   `active (exited)` unit is bookkeeping, not proof (`rules/law.md` item 9).
3. **Map the full assert chain** of the publication path (identity → CAS subset →
   generation → parse → schema → credential subset → readback) with owner and failure
   class per assert. Predict where the current fix will displace the symptom.
4. **Route orphaned transaction state to its owner.** A persisted intent from an earlier
   binary is a defect of the transaction-store owner, which rejects it with a typed
   error and owns its removal; no quarantine copy is kept (`rules/storage.md`).
5. **Fix at the owner, fix-forward.** Volatile fact classes (health, quota, suspension,
   credential-derived actives) belong in the CAS volatile set, not in snapshot freezing;
   a race's root cause is fetch→publish non-atomicity.
6. **Close with bead evidence**: exact commands, exit codes, and the chain map updated
   with which assert now fails (or none).

## Anti-patterns

- Redeploying dist from source without re-proving binary compatibility.
- Trusting `systemctl is-active` twice before checking the port.
- Whole-blob diffing when a field-level diff isolates the cause in one read.
- Daemon retry loops to absorb a race the publisher should fix in-cycle.
