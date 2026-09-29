# 20260929: fleet coordinator handoff

## 1. Mission

The mission is P0 before any new phase:

1. Integrate every lane.
2. Retire lanes that are not active.
3. Turn the three P0 red tips green: the flext root `0.12.0-dev`, cosmos-main
   `develop`, and cosmos-docgen `dev`.

A phase counts as closed only when CI is green, the PR is merged, post-merge
proof exists, and the bead is closed with evidence.

## 2. Rulings and laws in force

| Item | State |
|---|---|
| Adopt the cosmos-main direct push `c2324a0f3` ("dev") as base, fix-forward | **Operator-approved 2026-09-29.** Pusher recorded: GitHub `marlon-costa-dc`, PushEvent 2026-09-28T22:04:47Z, no PR (bead `cosmos-7ysc5`) |
| Merging with `make test` red | **Forbidden.** R-S3 (`docs/rules/session-execution-rules-20260927.md:18`, the PR goes up with tests green) and bead-branch-pr-cadence §4.1 (full suite before the PR exists) forbid it; AGENTS #14 makes every warning, skip or failure RED. The earlier coordinator ruling that allowed it (used for ai-hub #940/#941) was never operator law and is void |
| One merger per repository (the coordinator); workers deliver green PRs and never merge | Law of this handoff; the general rule is pending in `ag-k47r` |
| One heavy gate per machine (ADR-0021) | In force; the carve-out is pending in `ag-g29z` |
| ai-hub `main` frozen; no promotion | In force |
| Never hand-edit `.beads/config.yaml` (flext-infra projection) or commit with `core.hooksPath` overridden | In force; the rule is pending in `ag-4a82` |
| Claim a bead only with a worktree and a first commit | In force |
| flext-infra #938: (a) `make dev` composite verb, (b) `project.dependency_sources` Git overrides | **Pending the operator.** The coordinator recommends rejecting both |

## 3. Measured state at handoff (2026-09-29 ~01:30Z)

- **flext root `0.12.0-dev`** at `b075f13dd`: CI cancelled (36365188009), Docs
  failed (36365188017). The flext-infra gitlink `0cdeaf4eb` is 389 commits
  behind the infra tip. `uv.lock` resolves members as workspace editables, so
  the root is pinned by its gitlinks; the lock only needs a relock after they
  move. #289, #296 and #297 are BLOCKED on `ci`.
- **flext-infra `0.12.0-dev`** at `8b37da306` (#1056): CI green. Its ci.yml
  runs no pytest step, so test reds stay hidden: `flext-qsou4`, the
  boundary-gate fixture, and the Bandit severity bug.
- **ai-hub `dev`** at `021f6e008` is 39 ahead of `main` (`0e66c1960`, which
  carries #836 against the operator's NO). #946 was merged by the ai-hub
  merger session at 01:10:10Z (a56e053d7); no ai-hub PR is open.
- **cosmos-main `develop`** at `c2324a0f3` fails at setup: the retired
  `datacosmos-br/flext-web@baseline-20260919` cannot be fetched. #304 passes
  setup and fails the gen fixed point; #303 is superseded by #304 except its 3
  `[WIP]` bootstrap commits.
- **cosmos-docgen `dev`** at `dd351adfa` fails the gen fixed point: export
  collision for `s` (`dcdoc.api` vs `dcdoc.base`).
- **cosmos-gitops** tip is a helm-semver[bot] `[skip ci]` commit (writer defect
  in `cosmos-cd3mh`).

## 4. Work preserved this session (all on remotes)

| Lane | Repo / branch | Head | Bead |
|---|---|---|---|
| t8p7n | flext-infra `fix/flext-t8p7n-forbid-gate-suspension-20260928` | 67049cac4 | flext-t8p7n (absorbs the flext-d3nwq fixture hunk) |
| pr938 | flext-infra `adopt/pr938-20260928` | 6130f35cd (20 edits, unvalidated) | flext-m3sre |
| qlty attestation | flext-infra `fix/qlty-attestation-enable-20260928` | 27251093c | flext-38odd |
| nktqo | flext-target-ldap `fix/flext-nktqo-mypy-resource-20260928` | 21fca19 (make upg output) | flext-nktqo |
| cosmos-7ysc5 | cosmos-main `lane/cosmos-7ysc5-develop-ci` | e04d26a82 (develop + #304) | cosmos-7ysc5 |

The dirty root trees (`root-tip-green-r4`, `root-launcher-sync`,
`gdm8w-root-repro`) hold only gitlink moves and regenerable projections. They
are classified on `flext-itpd1.3.14` and `flext-hfv64` and are disposable after
the root lands.

## 5. Resume queue (P0 order)

Each item follows the same cycle: local green gate, then PR, then green CI,
then the coordinator merges, then the post-merge tip CI is checked. One heavy
gate runs at a time.

1. **flext-infra tip green.** `max-failures: 1` stops every lane at the first
   tip red, so this blocks all infra lanes. The cold `make test` on 8b37da306
   (01:11Z) shows three reds: the two `abstraction_boundary` fixture failures
   (fixed in the t8p7n lane) and `flext-u7w1d`. `flext-pxonf` was re-measured:
   at load ~4 the cold DB warms (0 to 1.28 MB). What remains is the cold
   full-suite budget: about 450s on 4 workers against 120s.
2. **flext-infra, one at a time** (t8p7n + u7w1d first):
   - `flext-n6y4i`: pushed as `fix/flext-n6y4i-single-mise-reader-20260929`
     (09fc54b8a). One parent-walking reader; the fixtures seed through
     `u.Tests.copy_tracked_mise_seeds`. Dependents: `flext-ezzws`,
     `flext-qsou4`.
   - `flext-t8p7n`.
   - `flext-idihq` (WIP 47bdff5b6).
   - `flext-akfj4`, `flext-7gdlg`, `flext-zmzvq`, `flext-dkoe4`.
   - `flext-38odd`.
   - `flext-abv33`: derive gate applicability, then delete the empty-target
     skip/receipt paths (`base_gate.py:70-80`, `pyright.py:26-50`,
     `pyrefly.py:27-159`, `bandit.py:43-52`).
   - `flext-m3sre` (#938, minus the pending (a)/(b)).
   - `flext-t3gku`: the detector at `workspace/detector.py:528` must fail loud
     on an empty gitlink directory.
   - `flext-u7w1d`: `test_resource_limits[memory-1]` exits 2 instead of 1 on
     Linux; it blocks the tip together with the t8p7n fixture reds.
   - `flext-nktqo` (flext-target-ldap mypy gate killed at 6144 MiB/100s):
     profile first; the pushed `make upg` output (21fca19) is re-derived on the
     current infra tip, never promoted as is.
3. **Root (`flext-itpd1.3.14`, claimed):**
   - Work in a fresh root worktree from `origin/0.12.0-dev`.
   - Move the flext-infra gitlink to at least 8b37da306.
   - Run `make upg`, then `make gen` twice (the second run must produce no
     diff), then `make check` and `make test`.
   - Push fast-forward to `fix/root-tip-green-20260928` (#289) and get CI and
     Docs green. Merge.
   - Then #296 (`flext-hfv64`; `bin/mise:24` still resolves `releases/latest`)
     and #297.
4. **flext-core #523** (`flext-blgw9`): merge once green. Then `flext-sdjub`
   and `flext-lwvy1`.
5. **ai-hub:** #946 has been merged; the ai-hub merger session owns that repo's merges. `aihub-kvx0x.6.6` and `aihub-kvx0x.6.7` are blocked on the operator's
   OAuth for native agent acceptance.
6. **cosmos-main (`cosmos-7ysc5`):**
   - Run `make upg` to move off the retired datacosmos pins.
   - Prove the gen fixed point in CI mode.
   - Fix the npm warnings (they are RED; this reopens the scope of
     `cosmos-fplq3`).
   - Land it, then close #303/#304.
   - Then the cosmos-docgen `s` collision at the dcdoc owner.
   - Then the cosmos-gitops helm-semver writer: remove `[skip ci]`.
7. **Fleet cards:** the 26 finish-and-close cards (gc-wisp-6pdozy) go to the
   fleet through gc mail.
8. **Retirement:** after ancestry proof against a freshly fetched base, retire
   flext-1um47, flext-gdm8w, ai-hub-work/ua5wb, ai-hub-work/r4 (xgq4t,
   merged), flext-d3nwq, and the three dirty root trees.

## 6. Pending operator decisions

1. ai-hub `main` after #836 (0e66c1960); dev and main have diverged.
2. #933 runtime_census vs the 2026-09-16 contract.
3. gascity fast-forward: 413 behind `origin/dc-use`; it deletes runtime links.
4. DataOP #10 (the stale lock).
5. algar-oud-mig `.beads/identity.toml`.
6. The flext-infra primary's local branch, 5 ahead (a ref move).
7. #938 (a)/(b), see §2.

## 7. Critique of the previous coordinator window (condensed)

| Theme | Defect | Rule | Correction |
|---|---|---|---|
| Merge authority | About 12 workers merged whenever ready; the flext-infra freeze was broken 4 times | parallel-delegation.md:23, fanout-qa-publication | One merger per repo; `ag-k47r` |
| Load | Load 55-68 on 20 cores; timeouts produced false reds (t8p7n, idihq, gdm8w) | heavy-gate-serialization (ADR-0021) | One heavy-gate slot; `ag-g29z` |
| Tracker | 16 claims made at the same second with no worktree; duplicate beads (s64n2/bv8gs, d3nwq/t8p7n); merged work left in_progress | bead-branch-pr-cadence §1-3 | Fixed this session: released 10 flext and 15 ai-hub claims; closed 1um47, gdm8w, xgq4t; superseded d3nwq; contradictions filed as `ag-e3ul`, `ag-h31o` |
| Test law | Merges with make test red; infra CI has no pytest | AGENTS #14, R-S3 | Ruling void (§2); `flext-pxonf` is first in the queue |
| Projections | `.beads/config.yaml` hand-edited (gmn#64, mcb#262); `core.hooksPath=/dev/null` commit (ccs-51, unpushed) | generators-not-projections, gitflow-branch-pr | `ag-4a82`; redo ccs-51 with hooks |
| Root chain | 5 hours of hypotheses before reading the root gitlink and Makefile | integration-propagation-chain H1 | The root pins members by gitlinks; move the gitlink first |
| Handoff | A home-file ledger instead of a versioned directory | plan-handoff, plan-topic-monopoly | This directory; `ag-c0vo`; `ag-xd1y` for the gascity §5 retry text |
