# Session Retro — zcode fleet session 2026-09-26/27

## What went well

- Lanes A+B+suite-green consolidated: 56F/5E/6S/111W → all cured at owners
- Rope fork dc.3 deployed with PEP 701 tokenizer cure (no monkeypatch)
- 5 SSOT collapses landed (PRE_COMMIT_CONFIG, isolation keys, docs_config, Makefile dupes, asset-surface dedup)
- Hook-runtime verbs wired through the SSOT (PRs #896/#898)
- Catalog TTL cache landed (PR #902) — no more per-cycle remote fetch stall
- 111 model-governance warnings eliminated at the model source
- Per-platform resource-limit contracts (6 skips → 0)
- ai-hub ADR-0031 (model-pipeline provenance reset) recorded on the hooks-runtime lane (PR pending); the census ruling consolidated into ADR-0028, its coordinated duplicate (agents ADR-0031) retired at the dev merge

## What went wrong — and the structural fix for each

| Failure | Root cause | Fix |
|---|---|---|
| Executed another agent's plan (proxy/pipeline) | Didn't verify plan ownership | Always check bead claims + gc-mail before acting on a plan |
| Agent swarms with overlapping mandates on one lane | No single-writer-per-lane check | R-S2: verify mtime + bead claim before touching a lane |
| Worktree swept while agent worked inside | Didn't commit/push for >15 min | R33: commit+push at every green milestone, max 15 min |
| PR opened with check red | Validated after pushing instead of before | R-S3: validate before pushing, CI confirms |
| plans rejected as weak/headless | Planned before reading contract/rules | R-S1: read bases first, then plan |
| Bead hygiene only after 3 orders | Beads treated as diaries not claims | R-S6: beads are claims — heartbeat ≤1h |
| Tests treated as oracle | Runtime more stable than tests | R-S5: runtime is the oracle, tests are witnesses |
| Accepted slow (45-70s setups) | No timeout enforcement | R-S4: every execution has a timeout |

## Structural fix: skills that prevent these failures

| Failure pattern | Preventing skill |
|---|---|
| No bead claim before acting | `coordination-protocol` |
| Running production daemons directly | `runtime-validation` (deployment lifecycle only) |
| Worktree swept mid-work | `lane-adoption` (15-min push cadence) |
| Slow setups accepted as normal | `runtime-validation` (measured timeouts) |
| Plans rejected for missing contract review | `session-preflight` (read before plan) |
| Tests as broken as runtime | R24: no mocks, real adapters only |
