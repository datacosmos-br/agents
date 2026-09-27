# 20260927 — Handoff: ai-hub runtime activation (provenance reset + pipeline READY + hooks wiring)

Session: zcode (this session's durable record; the ai-hub repo carries the same content via PRs #896/#898 and the docs lanes).

## 1. Mission

Make the ai-hub model-pipeline runtime actually work end-to-end: provenance reset in the CLIProxy fork, inventory contract alignment, pipeline bootstrap to generation 1, install ×2 idempotent, hooks-runtime verbs wired through the CLI SSOT, enforcement gated on the native proof.

## 2. State (all measured, evidence paths inline)

| Layer | State | Proof |
|---|---|---|
| Provenance (CCS) | CLEARED — `model_pipeline:` block removed from `~/.ccs/config.yaml` via the fork's `DELETE /api/config/model-pipeline` (agent implemented the endpoint; binary rebuilt WITH stamping ldflags, swapped with backup, restarted 2026-09-27 14:04) | `/home/marlonsc/tmp/v8/provenance-unblock2/` |
| Inventory (dc12) | Validates against `AiHubModelPipelineInventory` after the stamp rebuild (the unstamped build emitted `built_at: "unknown"`) | `provenance-unblock2/15-inventory-model-valid.txt` |
| Catalog resolution | 17/17 dc12 claude models normalize to unique `anthropic/*` entries (graph channel-identity normalization landed: commit `1119ea785`) | contract tests 37/37 |
| Snapshot assembly | FAILS on `claude/claude-3-5-haiku-20241022` — no resolved catalog model in models.dev for that pair. THE remaining blocker | journal 14:54+ |
| Hooks units | socket ACTIVE; service dies `243/CREDENTIALS File exists` on every start (LoadCredentialEncrypted ×4, sources intact; runtime dir cleared, recurs) | escalated to the coordinator (gc-mail, delivery proven) |
| Install ×2 | Blocked behind the snapshot assembly | — |

## 3. The remaining cure (one blocker, owner named)

`claude/claude-3-5-haiku-20241022` has no models.dev identity. The graph builder (commit `1119ea785` on `fix/hooks-runtime-verbs-route`) normalizes channel-identity keys on both branches; the haiku pair needs the catalog side to carry the `anthropic/claude-3-5-haiku-20241022` identity (models.dev entry) or an explicit alias rule in the catalog resolution owner (`src/ai_hub/services/model_pipeline/graph.py`). After that: snapshot V3 validates → PUT ccs:3184 (CAS + projector) → `active.json` → `make install` ×2 → READY.

## 4. Rules applied (04-regras V8; the conduct contract)

- R23: validate before push (gen×2, check, tests green on the lane head; CI confirms).
- R24: tests with zero tolerance — no mock/fake/skip; real adapters through the public interface.
- R25: 120s per invocation; slowness is a defect cured at the owner.
- R26–R32: SSOT single-owner; StrEnum in `c`; zero model-creation helpers; validation native in the model (Pydantic 2); models AS-IS by inheritance/composition; SOLID/DRY blocking.
- R33: landing cadence ~15 min with the tip, merge `--no-ff`.
- D-ASK: critical doubt → stop and ask the coordinator (it escalates to the human operator).

## 5. Coordination record (gc-mail human, delivery proven)

1. `[coord] lane claim ai-hub-worktrees/hook-runtime-verbs-routes feat/hook-runtime-verbs-routes + rules concern re fix/hooks-runtime-verbs` — lane claimed; rules concern recorded on bead `aihub-kvx0x.6.4` (no claiming bead on the lane; half-applied cure published; locks uncommitted for hours).
2. `[coord] gen fixed-point break: generated docs artifact dropped by a merge on hook-runtime-verbs-routes` — the missing `projects/index.md` root cause + the rule (generated files are never deleted in merges; gen×2 before committing merges).
3. `[coord] critical doubt: ai-hub-hooks.service dies 243/CREDENTIALS File exists on every start` — full measurements; owner: the credential provisioner.
4. `[coord] status zcode: bead aihub-kvx0x.6.4 active` — the standing status chain (multiple updates, all delivery-proven).

## 6. Open items (owners named)

1. Catalog resolution for `claude-3-5-haiku-20241022` — agent in flight on `fix/hooks-runtime-verbs-route`; the models.dev identity is the fact to verify.
2. `ai-hub-hooks.service` 243/CREDENTIALS — host credential provisioner owner (escalated; mail in the human inbox).
3. flext-infra PR #902 — open (SSOT wiring + reconciliations); ci/Kilo were pending at handoff.
4. flext-infra census/namespace (170+142) — the active sessions' #920/#922 cure program.
