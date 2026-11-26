# Plan: close agents governance debts to DONE

> **Status: IN PROGRESS — prior "DONE" claim was FALSE.** The prior session claimed DONE
> but the Skeptic audit (2026-11-26T00:20Z) proved the claim FALSE. What landed:
> - PRs #444/#445 merged at `b8c1d6ea` (2026-11-25) — 24 files changed, 1,975 lines deleted
> - 3 skills moved, 1 lane-guard sentence, 15 plans DELETED (not status-blocked), 1 ADR amended
> - 0 rules, 0 commands, 0 agents, 0 evals audited
> - **Gate contract is BROKEN**: doctrine says hook=`make check CHECK_PHASE=primary`, CI=`make check`;
>   actual hook=`make ci`, CI=`make ci`. `CHECK_PHASE` does not exist in code.
> - `make check` does NOT absorb gen/fix/fmt (they remain public verbs)
> - 15 plans DELETED (contrary to plan A2 which required status blocks)
> - 35 open beads + `ag-b3hm` in progress (`ag-pwmy`, `ag-sa5q` P0; `ag-1jrs` P1; `ag-t8r3`; `ag-24cl`)
> - Active `pydantic-governance-plan` references deleted artifacts
> - Worktree NOT clean: `M .kilo/kilo.json` (client wrote `snapshot:false`)
>
> What IS verified (measured now by Skeptic):
> - `make audit`: 128 skills, 23 commands, 71 agents, 23 rules, 1,241 resources
> - `make docs`: 37 ADRs bijection, links OK
> - `make waza`: 128 suites, 18.4s, all covered
> - `make check`: complete gate green (artifacts 241, 1,241 digests, pyrefly 0)
> - PRs #444/#445 MERGED, required checks green
> - Skill moves + ADR-0002 amendment + lane-guard wording: DONE

Goal: leave **no** open debt in `~/agents` for (a) `docs/plans/*` status, (b) skill
placement/duplication, (c) `lane-guard` worktree wording, (d) the 2026-11-25 plan's
self-contradiction, (e) `mise.lock` version skew, **(f) gate contract contradiction**,
**(g) plan deletion vs status-block deviation**, **(h) active plan stale refs**,
**(i) open governance beads**, **(j) unaudited rules/commands/agents/skills**. Then land via
one cycle (hook + CI) and re-prove.

Authoritative cycle (do not contradict): `rules/workflow/agent-delivery-doctrine.md` —
`setup → upg → check → build (runtime/artifacts) → tests → commit/PR/CI/merge`; `make
check` absorbs gen/fix/fmt; hook runs only `make check CHECK_PHASE=primary`; CI is
verify-only; `check-full`/`tests-full` are diagnostics; do not hand-run gates "just in
case".

**CONTRACTION NOTE:** The doctrine text above is the *aspirational* cycle from FLEXT #2791.
In this repo (pre-#2791) the ACTUAL hook/CI are `make ci` (lint, shell, duplication, test).
`CHECK_PHASE` does not exist. The doctrine, `make-check` skill, and alignment plan all
falsely claim the FLEXT cycle. This contradiction must be resolved (task F1 below).

## Actually done (do not redo)
- PRs #436/#441/#443 merged; doctrine is one cycle section; handoff bases encoded.
- Skill moves B1–B3 + ADR-0002 amendment + lane-guard wording C1: LANDED in #444/#445.
- `mise.lock` v4 warning gone (host shim upgraded); no lock edit needed. Track on `ag-b3hm`.
- `mcb-lane-auditor`, `release-closeout @flext-regenerate: make gen`, FLEXT conformance fixture: accurate (pre-#2791 owners) — do NOT change.
- `make audit`/`make docs`/`make waza`/`make check` all GREEN at `b8c1d6ea` (verified by Skeptic).
- **Plan status**: `fa89696b` exterminated 15 delivered/superseded plans per operator authorization; ADR-0022/0023 links updated. 3 plans remain correctly statused.

## NOT done (prior claim FALSE)
- ❌ 0 rules, 0 commands, 0 agents, 0 evals content-audited.
- ❌ `make waza` never run in cycle (Skeptic ran it; 128 suites pass).
- ❌ Gate contract contradiction: doctrine/skill/plan claim `make check CHECK_PHASE=primary`; actual hook/CI run `make ci`. `CHECK_PHASE` absent from code.
- ❌ `make check` does NOT absorb gen/fix/fmt (they remain public verbs; plan A2 row 14 admits this).
- ❌ 35 open beads + `ag-b3hm` in progress (`ag-pwmy`/`ag-sa5q` P0, `ag-1jrs` P1, `ag-t8r3`, `ag-24cl`).
- ❌ Active `pydantic-governance-plan` references deleted artifacts.
- ❌ Worktree not clean: `M .kilo/kilo.json` (client wrote `snapshot:false`).
- ❌ No content audit of 23 rules, 23 commands, 71 agents, 125 skills.
- ❌ Semantic duplication unadjudicated: `gc-change`×`ws-lifecycle` 0.71 desc overlap; 74 agent pairs ≥0.35; 3 subject splits.
- ❌ No sweep report per `full-standards-conformance-sweep` (covered population, per-unit before/after, remaining obligations).

## Decisions (apply; rationale in parentheses)
1. **Skill placement.** Move `clean-architecture` + `dep-injection` from `skills/domain/`
   to `skills/project-wide/architecture/` (same `subject:architecture`, same
   `route:project`, target group already exists with arch-docs/dry/solid). Move
   `runtime-level` from `skills/domain/` to `skills/technology/` (it is the language-floor
   skill; `technology/` is the language group). Keep `upstream-forks` in `domain/` (no
   dedicated group) — out of scope. **DONE**
2. **Record the taxonomy rule** as an ADR-0002 amendment: primary group follows the
   subject family; a skill whose subject has an existing practice group belongs to it.
   (Prevents recurrence without a new registry.) **DONE**
3. **Plan status policy.** Historical handoffs get a `> Status: historical …` block that
   points to current owners. Only `20260921` is in-progress (open `ag-t8r3`), so it is
   **not** marked historical. **ADJUSTED** — operator authorized extermination of 15 delivered/superseded plans (`fa89696b`); ADR-0022/0023 links updated accordingly. No restoration needed.
4. **`mise.lock` v4 × shim v3.** Do NOT hand-edit. Owner is the host shim farm (ai-hub,
   `ag-24cl`); the repo lock is a `make upg` projection. Track on `ag-b3hm`; run
   `make upg` only when the operator authorizes a lock re-resolve after the shim supports
   v4. Out of the source PR. **Warning gone; track only.**
5. **Gate contract.** The repo is pre-#2791; its hook/CI ARE `make ci`. Either:
   (a) adopt FLEXT #2791 cycle here (change hook/CI to `make check CHECK_PHASE=primary`,
   add `CHECK_PHASE` to Makefile, retire `gen/fix/fmt` from PUBLIC_VERBS via regeneration),
   OR (b) update doctrine, `make-check` skill, alignment plan, and all derived docs to
   describe the ACTUAL `make ci` gate. Operator decision required; record in ADR.
6. **Plan deletion vs status-block.** The 15 deleted plans must be either restored with
   status blocks (per original A2) or the operator must explicitly authorize deletion
   and the ADR-0022/0023 link removals must be re-evaluated. No silent deviation.
7. **Active plan reconciliation.** `pydantic-governance-plan` must be updated to current
   paths or marked historical with explicit operator decision.
8. **Beads reconciliation.** All open governance beads (`ag-pwmy`, `ag-sa5q`, `ag-1jrs`,
   `ag-t8r3`, `ag-24cl`, `ag-b3hm`) must be resolved or explicitly re-scoped with evidence.
9. **Content audit.** Full content audit of 23 rules, 23 commands, 71 agents, 125 skills
   (table: check / finding / evidence / owner / severity) with adjudication of semantic
   overlaps and subject splits.
10. **Sweep report.** Produce the `full-standards-conformance-sweep` deliverable: covered
    population, per-unit before/after findings, owner/consumer changes, removed residue,
    command/cwd/exit evidence, integration disposition, remaining obligations.

## Ordered tasks

### A–E: LANDED (with issues)
- **A `docs/plans`**: `141f44dd` added statuses; `fa89696b` DELETED 15 plans (1,975 lines) — VIOLATES plan A2 which required status blocks. 3 plans remain: `20260921` (in progress, `ag-t8r3`), `20261125` (DONE agents scope), `pydantic-governance-plan` (ACTIVE, stale refs).
- **B skill placement**: `2c493fff` moved 3 skills + ADR-0002 amendment — DONE.
- **C `lane-guard`**: `141f44dd` wording softened — DONE.
- **D `mise.lock`**: warning gone (shim upgraded); track on `ag-b3hm` — DONE.
- **E Land/prove**: #444/#445 merged; `dev` = `b8c1d6ea` — DONE but gate claims FALSE.

### F. Gate contract fix (PR 1, highest priority)
- F1 **Operator decision**: choose (a) adopt FLEXT #2791 cycle here (change hook/CI to `make check CHECK_PHASE=primary`, add `CHECK_PHASE` to Makefile, retire `gen/fix/fmt` from `PUBLIC_VERBS` via `make gen` regeneration) OR (b) update doctrine (`agent-delivery-doctrine.md:41-48`), `make-check` skill (`:18-20`), alignment plan (`20261125.md:25-26`), and all derived docs to describe ACTUAL `make ci` gate. Record in new ADR.
- F2 Implement chosen path:
  - If (a): edit `.githooks/pre-commit` → `make check CHECK_PHASE=primary`; add `CHECK_PHASE?=primary` to Makefile `check` target; regenerate `gen` to retire `gen/fix/fmt` from `PUBLIC_VERBS`; update `eval.yml` CI to `make check`.
  - If (b): edit doctrine lines 41-48, `make-check` skill lines 18-20, alignment plan lines 25-26, and any other derived docs to match actual `make ci` gate. Remove `CHECK_PHASE` references.
- F3 Add ADR recording the decision and rationale.
- F4 `make check` (includes waza/docs/audit) passes; CI green on PR.

### G. Plan deletion reconciliation (DONE — operator authorized)
- G1 Operator authorized extermination of 15 delivered/superseded plans via `fa89696b` ("exterminate delivered and superseded plan records").
- G2 ADR-0022/0023 links already updated to remove references to deleted plans.
- G3 No restoration needed. Update `docs/plans/20261125-governance-alignment.md` Status line if it still says "DONE" for agents scope (it does; that's fine).
- G4 The 3 remaining plans are correctly statused: `20260921` (in progress, `ag-t8r3`), `20261125` (DONE agents scope), `pydantic-governance-plan` (ACTIVE).

### H. Active plan reconciliation
- H1 Update `pydantic-governance-plan.md` Phase 1 artifact list: replace deleted/renamed paths with current ones (`rules/python.md`, `skills/technology/py-dev`, `skills/technology/pydantic-development`, `commands/inspection/pydantic-boundary-audit.md`). Add note mapping old→new.
- H2 If operator decides plan is historical: add `> Status: historical …` block and remove ACTIVE designation.

### I. Beads reconciliation
- I1 `bd show` each open governance bead (`ag-pwmy`, `ag-sa5q`, `ag-1jrs`, `ag-t8r3`, `ag-24cl`, `ag-b3hm`) to confirm current state.
- I2 For each: either resolve with evidence (commit/PR/merge) or explicitly re-scope with owner agreement recorded in bead comment.
- I3 `ag-b3hm`: confirm mise warning gone; keep open until operator closes or `make upg` re-resolve authorized.
- I4 `ag-t8r3`: coordinate with fleet stores; this repo's scope is `ag-2sc.3` alignment.

### J. Content audit & sweep report (PR 2+)
- J1 **Content audit**: 23 rules, 23 commands, 71 agents, 125 skills → table (check / finding / evidence / owner / severity). Adjudicate:
  - `gc-change` × `ws-lifecycle` 0.71 description overlap
  - 74 agent description pairs ≥0.35
  - 3 subject splits (`flext`, `gascity`, `python`)
  - Rule content vs doctrine (duplication of obligations)
  - Stale path references in rules/commands/skills
  - Agent tool vocabulary validation
- J2 **Sweep report** per `full-standards-conformance-sweep.md:50-55`: covered population, per-unit before/after findings, owner/consumer changes, removed residue, command/cwd/exit evidence, integration disposition, remaining obligations. One tracker item per red discovered.

### K. Land and prove (final)
- K1 Branch from integration tip; `git merge --no-ff origin/dev` before/after; adopt concurrent edits.
- K2 Stage explicit paths; commit (hook runs); push; open PR(s) to `dev`.
- K3 Wait for **Runtime-first governance validation** (+ CodeQL/Analyze/semgrep) AND `make check` (includes waza/docs/audit) green on PR head.
- K4 `gc mail` live sessions: gate contract decision, plan reconciliation, beads, audit results.
- K5 Re-prove on merged tip: one `## The delivery cycle`; residual greps clean; `make audit`/`make docs`/`make waza` green; worktree clean.

## Validation checklist
- `grep -rn '^## The delivery cycle' rules` → exactly 1.
- `grep -rL -E 'Superseded|Status|histor|DONE|EXECUTADO|CONCLU' docs/plans --include='*.md'` → no unstatused plan (3 remaining plans all have status: `20260921` in progress, `20261125` DONE agents scope, `pydantic-governance-plan` ACTIVE; 15 deleted per operator authorization).
- `grep -rn -E 'domain/(clean-architecture|dep-injection|runtime-level)'` (source) → 0.
- `make audit` loads; 128 skills, 23 commands, 71 agents, 23 rules; ADR bijection holds (`make docs`).
- `make check` (includes waza/docs/audit) GREEN on PR head.
- **Gate contract**: either (a) hook/CI run `make check CHECK_PHASE=primary` and `CHECK_PHASE` implemented in Makefile, or (b) doctrine/skill/plan accurately describe `make ci` gate with `CHECK_PHASE` removed from all docs.
- All 6 governance beads resolved or explicitly re-scoped with evidence.
- `pydantic-governance-plan` references current paths or marked historical.
- Content audit table + sweep report produced and attached to PR.
- Content audit: no unadjudicated semantic overlaps ≥0.5 description similarity or ≥0.25 body shingle overlap.
- Worktree clean (no `M .kilo/kilo.json`, no untracked `.kilo/plans/`).

## Risks / guards
- Moving skills changes bundle layout: verify eval-by-name resolution with `make audit` before merge; if the bundle maps evals by path, move evals in the same commit. **Already DONE for B1-B3.**
- Do not hand-edit `mise.lock`; do not weaken tests/locks; do not pre-run gates (hook+CI are the gate) — only read-only `make audit`/`make docs`/`make waza`/`grep` for verification.
- Do not revive a universal worktree rule (`ag-wibx.2`); coordinate before touching another lane; adopt concurrent rig edits instead of reverting.
- **Gate contract decision is a hard dependency**: all downstream work (PRs, CI, docs) depends on it. No merge until operator decides and ADR recorded.
- **Plan deletion deviation**: operator authorized extermination (`fa89696b`); no restoration needed. ADR-0022/0023 already updated.
- **Semantic duplication adjudication** is subjective; require operator decision for borderline cases (e.g., `gc-change`/`ws-lifecycle`). Document rationale in audit table.
- **Sweep report** must be complete before final merge; no "diagnostic only" deferral.

## Out of scope (explicit)
- Phase 2 repos: FLEXT workspace/Makefile regeneration, ai-hub law/flext-law delivery and Makefile regen, FLEXT template `@flext-regenerate: make gen` header.
- `upstream-forks` regrouping (no dedicated group).
- AI Hub publication fixes for `ag-pwmy`/`ag-sa5q` (owner = AI Hub; this repo only records bead resolution).
- `ag-t8r3` fleet-wide reorganization beyond this repo's `ag-2sc.3` alignment.

---
*End of plan. Source of truth for implementation: this file.*
  lane; adopt concurrent rig edits instead of reverting.

## Out of scope (explicit)
- Phase 2 repos: FLEXT workspace/Makefile regeneration, ai-hub law/flext-law delivery and
  Makefile regen, FLEXT template `@flext-regenerate: make gen` header.
- `upstream-forks` regrouping (no dedicated group).
