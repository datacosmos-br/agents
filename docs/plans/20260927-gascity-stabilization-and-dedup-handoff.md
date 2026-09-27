# 20260927 — gascity stabilization + tracker dedup handoff (session ZCode)

Canonical record for the next session owning gascity/beads stabilization and the
tracker dedup role. Everything below was measured on this host and mirrored in
beads and gc mail (thread: gc-wisp-0plu55, e40ipf, 4m79c5, 32u1of, 8fzill,
cxz44c, 21lncf). The disposable handoff file
(`~/handoff-gascity-beads-20260927.md`) is only a pointer to this record and to
the beads below.

## 1. Landed (proofs on the integration line)

| Item | Proof |
|---|---|
| gascity PR #23 merged | conflict with dc-use resolved by no-ff adoption of the in-progress merge in lane `lane/dc-use-rebase-20260925`; doctor generations reconciled (3-arg `NewCustomTypesCheck`, `bdExecutable()` pinning, `startup-health-episode`) |
| gascity PR #24 merged | retargeted to dc-use per its own body; mergeable after #23 |
| gascity PR #22 closed superseded | only unique commit (`6c0a8e33`) is an older upstream sync |
| dc-use tip | `4caabdb66` (carries #23 + #24) |
| gascity bead | `gct-x4dgu` CLOSED (four sources) |
| ai-hub | #890 (A1 status-truth), #891 (pure DI root + public runtime hook), #894 (hook trace journal + in-window status red) merged into dev |
| flext | S1–S6 landed (#501–#514, cli #205, tests #131/#132); real slice state recorded on epic `flext-4jtcb` for ADR-019 (S7 not started; S2b dropped; S8/S9 landed untagged) |

## 2. Preserved branches (worktrees deleted, commits reachable)

`fork/convergence-python3`, `fork/docs-gc-mail`, `fork/dolt-cleanup-exact-target`,
`fork/release-ci`, `fork/staticcheck-v1.4.2`, `fork/supervisor-credentials`,
`fork/formula-tracked-branch`, `lane/integrate-v1.4.2-fc.1` (21 commits —
superseded predecessor integration lane, kept for audit).
Deleted as fully contained: `fix/rc-release-replace-owner`,
`lane/dc-use-v1.4.2-fc.1`, `fix/bd-dolt-sql-scope-flags` (#25 merged),
`landing/reval-dc-use`.

## 3. Tracker dedup role (running — claim `flext-09kci` / `gct-tsq2z`)

Law applied (operator order 2026-09-27): a bead untouched for >1h is abandoned —
including claimed/deferred/blocked. Close already-done/superseded with proof;
realign epics; fix titles; use `--force` when a lock blocks a justified operation.

- gascity: 20 abandoned formula scaffolds CLOSED (127 → 27 real); `gct-8ykop`
  title deduplicated; sheriff-review family inspected (related, not duplicates).
- ai-hub: `aihub-1ztxc` CLOSED (v5 chain concluded per its own authority file);
  `aihub-agfq7.4` CLOSED (31/31 fleet landing); `aihub-dcrzh` title realigned;
  `flext-1asfo` CLOSED OBSOLETE (protocols.py is member-maintained, not generated).
- flext (`flext-09kci`): 348 open, ZERO duplicate titles. BATCH 1 executed (4
  absorbed stabilization lanes disposed, 0-unique). BATCH 2 running: 13/72
  verified — 6 closed DONE with file:line/measurement proof (cxxha, 7bm38,
  jnn9n, 6szaq.7, oftik, hp82t), 7 genuine-kept with refreshed evidence (94d4y,
  kjozu detector hardcode at detector.py:417-420, voi85, w0d4v BLOCKED no-venv,
  ssnc7.5 zero 0.12.x tags measured, ylzom pending lane experiment). ~59 remain.

## 4. Continuation queue (in order)

1. flext BATCH 2 continuation (59 beads, same method: one decisive check per
   bead, close DONE only with file:line/measurement, genuine backlog stays with
   refreshed evidence).
2. ai-hub step 2 leg-2 (SystemdUnitProbe adapter owning the interrogation moved
   from the daemon runtime service + `t.Port` instance conversion of
   daemon_status + root builds both ports) — design on epic `aihub-5j4cw`.
3. ai-hub 2b (client writes the same JSONL + dead external-hook chain removal,
   ~820L, regen).
4. ai-hub steps 3/4 (hook daemon install to completion; model pipeline service
   with ports — also cures the down sink behind the session-learning reds and
   gives `AI_HUB_LOCAL_MODEL_TEST_CONFIG` its producer).
5. Lock upgrade + projection convergence AFTER the V8 base settles (measured:
   premature `make upg` renders site_name `flext`, gen exit 2).
6. Post-release: land the preserved fork branches; re-pin dotgascity packs.lock;
   upstream #6678 merge follow-up.

## 5. Environment runbook (measured gotchas)

- `mise trust` required after mise 2026.9.13 upgrades — untrusted config fails
  EVERY bd subprocess.
- Session shells under `gascity-supervisor.service` carry `INVOCATION_ID` —
  tests asserting non-unit behavior scrub via the `env_vars` seam.
- Push gate caps concurrency: `GC_PUSH_GATE_NO_CAP=1` bypasses for one
  invocation; the darwin-compile pre-push job can die with an empty log under
  load — retry once before diagnosing.
- ai-hub PR CI fails at the cross-repo credential mint
  (`CI_DEPENDENCIES_APP_*` absent in PR context) — non-code red, flagged to the
  coordinator/admins.
- Heavy gates under host load: serialize I/O-heavy suites; the fsync-margin
  family (aihub-hrr0a) is tracked at its owner — never raise budgets.

## 6. Working rules for any session taking this over

1. Coordination first: read gc mail + beads + open PRs before implementing;
   report bead+branch+PR identity to the coordinator at every boundary.
2. Beads updated at least hourly in every state; >1h stale = abandoned.
3. no-ff merges only; no rebase/force; fix-forward/adopt; explicit paths.
4. Runtime is the validation; tests replicate reality or they are defects.
5. Close/dispose only with per-item proof; never destroy others' work.
6. Phase advance only with CI green and PRs integrated into the integration
   branch; inactive worktrees deleted at phase end.
7. Flext-infra conflict zone and other sessions' active lanes: stay out until
   the coordinator reallocates.
