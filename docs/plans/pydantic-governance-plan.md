# Pydantic Governance Program — Living Plan

> Status: ACTIVE · Owner: operator request 2026-09-08 · Coordinator session of
> 2026-09-08 (landings below). This document is the execution reference base for the
> Pydantic governance documentation, skills, enforcement, and automated migration. Edit
> it in place at every phase boundary; record evidence under each phase before
> propagation.

## Status dashboard (2026-09-08, post-landing)

| Phase                        | Scope                                                                             | State                        | Evidence                                                                                                                                      | Bead                       |
| ---------------------------- | --------------------------------------------------------------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| 0 — mise root cause          | ai-hub generator: no lock regime, authed resolution                               | **DONE** (active in runtime) | commit `646975403` ∈ ai-hub `origin/dev`; `lockfile=false`, zero `locked`/`tool_config`, global lock absent, `mise install` exit 0 fleet-wide | (`.5` ai-hub part)         |
| 1 — governance docs          | rule + skill + command + evals (agents repo)                                      | **DONE**                     | merge `c11ffa08` on `dev` (+`cf76d6f9`); gates exit 0; bundle 121 skills; waza 121 suites 0 MISS                                              | (program base)             |
| 2 — facade exports           | `m.StringConstraints/SerializeAsAny/FailFast/Discriminator/InstanceOf/ValidateAs` | **DONE**                     | flext-core PR #441 merge `9e3d1628d` on `0.12.0-dev`; six symbols import-proven; 2649 pass / 13 pre-existing (byte-identical to base)         | `flext-vjj1s.1` CLOSED     |
| 3 — superproject pointers    | `AGENTS.md` + `flext-law` + gitlink rollup                                        | **DONE**                     | flext PR #207 merge `f751d6029`; `git ls-tree` proves gitlink `9e3d1628d`                                                                     | `flext-vjj1s.4` CLOSED     |
| 4 — enforcement + migration  | ast-grip rules (flext-infra) then `make mod` fleet migration                      | **OPEN — next**              | beads filed; `.2`/`.3` open; `.3` blocked by `.2`                                                                                             | `flext-vjj1s.2`, `.3` OPEN |
| 5 — mise.lock extermination  | generator + global + repos                                                        | **~70% DONE**                | ai-hub ✓, agents repo PR #127 `cf76d6f9` ✓; REMAINS: flext member `mise.lock` deletions + `.mise.toml.j2` unlocked confirmation               | `flext-vjj1s.5` OPEN       |
| 6 — agents↔FLEXT convergence | centralized Make + generated `.mise` + toolchain drift                            | **OPEN (epic)**              | owns: `--workspace` gate drift, `deferred-self-reference`, testmon+cov runner defect                                                          | `flext-vjj1s.6` OPEN       |

Program completion: foundation (docs/exports/pointers/runtime regime) **100% landed and
active**; enforcement+migration is the remaining core (~40% of total effort);
convergence is a separate follow-on epic.

> **Status update 2026-09-18 (measured, campaign agents):** every remaining item
> (`.2`/`.3`/`.5` remainder/`.6`) lives in the flext tracker (`flext-vjj1s.*`, DB
> externo) — dono flext/flext-infra, fora do repo agents. O lado agents deste programa
> (fases 0–3 e PR #127 da fase 5) está completo e ativo; nenhuma ação catalog-side
> pendente. Ver `20260918-status-ledger.md` para o grafo de bloqueios.

## Next actions (ordered queue, estimates are focused agent-work hours)

1. **`.2` enforcement rules** (flext-infra): 7 ast-grep rules for the removal catalog
   (`model_rebuild`, unjustified `model_construct`/`SkipValidation`,
   `serialize_as_any=True`, catch-normalized `ValidationError`, `json.loads`+validate,
   raw pydantic imports at consumers, v1 `@validator`) + registry + `mod-check` green.
   Est. **2–3 h**, one lane, one session.
2. **`.5` remainder**: sweep `mise.lock` from flext members (one mechanical lane;
   template confirmation). Est. **~1 h**. Can run parallel to 1.
3. **`.3` automated migration**: run `$pydantic-boundary-audit` per repo → inventory →
   `make mod` batches → owner-side semantic fixes → gates. Volume-dependent ("thousands
   of violations" reported): est. **6–12 h across 2–3 sessions**, fleet-stabilization
   cadence (land per repo, never batch unreviewed).
4. **`.6` convergence epic**: Make control plane adoption in agents repo + the three
   standalone-toolchain drift fixes (owned here). Multi-day; file sub-beads when
   starting.

Dependencies: 3 after 1; 4 independent; 2 independent.

## Goal

One canonical Pydantic 2 (project floor: declared dependency SSOT; workspace installs
2.14.0b1, stable line 2.13.5) practice base for the fleet: how models are declared in
`m` with obligatory MRO presets, how protocols are declared in `p`, how conversions from
dict/TypedDict/dataclass/JSON are performed, how validation and serialization are used,
when read-only vs mutable vs strict base models apply, how identity models
(id/timestamps/version) are used, how typing composes with `p` and `r`, how `settings`
(runtime-adjustable) and `config` (static rules) feed `c`/`t`/`p`/`m`/`u`, the complete
good/bad practice catalog — including the demonized `model_rebuild` (a strict fleet
never needs it) — and the automated migration that removes the bad practices from fleet
code.

## Discoveries (living)

- 2026-09-08: concurrent diet renamed skills to short slugs with `supersedes:` lineage
  (`python-development` → `py-dev`); Phase 1 edits target the current tracked names.
- Known violation pressure: the operator reports thousands of facade/MRO violations
  fleet-wide; enforcement (Phase 4, bead C) and the automated migration (bead D) are the
  response.
- 2026-09-08: mise root cause chain: the ai-hub generator (AiHubMiseConfigService)
  forced `lockfile=true` + `tool_config.locked=true`
  - `mise lock --global --bump` while its GitHub resolution was unauthenticated (403
    rate limit), leaving a stale global lock that broke `mise install` fleet-wide;
    operator ordered extermination of the lock regime (fleet runs unlocked and current);
    fix branch `fix/extinguish-mise-lock`.
- 2026-09-08: execution model: main session acts as coordinator; bounded changes are
  dispatched to subagents; simple foreground edits continue in the main session.

## Phase 1 — Governance documents (`agents` repo, lane `feat/pydantic-governance`)

Artifacts:

1. `rules/python/pydantic.md` — distilled obligation rule (globs `**/*.py`).
2. `skills/technology/pydantic-development/SKILL.md` — router skill, extends
   `$python-development`, detects `pydantic`/`pydantic-settings`.
3. `skills/technology/pydantic-development/references/procedure.md` — the full
   reference: facade law, model MRO (obligatory), `p` protocol declaration (obligatory),
   preset decision table (read-only/mutable/strict), identity models
   (id/timestamps/version), inheritance and MRO rules, conversions
   (dict/TypedDict/dataclass/JSON), validation, serialization, `p`+`r` typing,
   performance, experimental policy, advanced types, anti-catalog, gates.
4. `skills/technology/python-development/SKILL.md` — compose `$pydantic-development`
   when the project declares Pydantic.
5. `skills/framework/flext-development/references/procedure.md` — Pydantic paragraph
   points at the new skill, presets, and TypeAdapter-once owners.
6. `commands/inspection/pydantic-boundary-audit.md` — read-only audit that inventories
   violations per repository and feeds Phase 4.
7. `evals/pydantic-development/` — suite + basic/edge/should-not-trigger tasks.

Evidence (fill at completion):

- [x] `make setup` — exit: 0 (mise install unlocked + uv venv + sync; unblocked by the
      Phase 0 mise lock extermination)
- [x] `make fix` / `make fmt` — exit: 0 / 0 (24 files unchanged)
- [x] `make check` — exit: 0 (GovernanceBundle.load: 121 skills incl.
      pydantic-development; waza: 121 suites, 0 MISS; installed wheel proof
      `ARTIFACT 0.4.0 … 121`)
- [x] `make test` — exit: 0 (typed incremental testmon cache hit: 4/4 deselected,
      integrity=ok, complete deselection accounting, warnings=0)
- [x] Runtime proof (bundle load / audit command load) — exit: 0 (check `audit` stage;
      command catalogued: 12 commands incl. pydantic-boundary-audit)
- [x] Propagation: merge commit onto `dev`, push — SHA: lane `2b51f60e` (merge commit
      SHA is the parent record on `dev`)

Phase 1 gate repairs adopted into this lane (pre-existing dev red, fixed at root): three
`skills/tool/*-session-extract`/`session-resume` frontmatters migrated to the closed tag
grammar v2 (dead `policy:*`/`provenance:*`/`tool:*`/ `updates:*` namespaces removed,
`subject:agents` added).

## Phase 2 — flext-core facade exports (lane in `flext-core`)

Export the stable advanced declarations through `m` so the rule is executable without
direct imports: `StringConstraints`, `SerializeAsAny`, `FailFast`, `Discriminator`,
`InstanceOf`, `ValidateAs` (all present in the installed floor). Facade exposure test
through the public `m` surface.

Evidence (recorded at completion — 2026-09-08):

- [x] Runtime proof `from flext_core import m; m.StringConstraints …` — exit: 0 (all six
      symbols printed, worktree src at lane tip `02b9dec46`)
- [x] Gates — member gates at lane tip: fmt exit 0; fix/check RED on pre-existing
      standalone-toolchain drift owned by flext-infra (bead `flext-vjj1s.6`:
      `flext-infra check run --workspace` unsupported by the resolved wheel; concurrent
      agent's in-flight Makefile carries the fix); test collection blocked by a
      concurrent agent's UNCOMMITTED `pyproject.toml` (removed `core` marker); full
      committed-content suite: 2649 passed / 13 failed byte-identical to integration
      base (verified set-diff on base `c2512e5c5`) — zero lane-introduced regressions
- [x] Propagation — PR #441 merge commit `9e3d1628d` on `0.12.0-dev` (parents
      `c2512e5c5` + `02b9dec46`), ancestry exit 0; gitlink rollup via superproject PR
      #207; lane branches retired (remote auto-deleted)

Lane notes: the concurrent agent's root fixes (containers owner refs, dup import, `core`
marker, I001 adoption, ContainerCreationOptions schema, lazy `__getattr__` publish
contract) were adopted as lane commits — joint work absorbed, not duplicated.

## Phase 3 — Superproject law pointers (lane in `flext`)

- Root `AGENTS.md` Conventions: one paragraph pointing at the skill, presets, and
  conversions owners.
- `.agents/skills/flext-law/SKILL.md`: Pydantic delta references the skill.
- Hunk-by-hunk adoption: `AGENTS.md` carries concurrent WIP; commit scoped hunks only.

Evidence (recorded at completion — 2026-09-08):

- [x] Gates — n/a (docs-only + gitlink; bundle/gates green through the agents-repo Phase
      1 cycle; superproject content verified post-merge)
- [x] Propagation — PR #207 merge `f751d6029` on `0.12.0-dev`;
      `git ls-tree HEAD flext-core` → `9e3d1628d…` (gitlink proven);
      `AGENTS.md`/`flext-law` clean of concurrent WIP at commit time (hunk isolation not
      needed — WIP had been committed by the concurrent lane)

## Phase 4 — Beads + automated migration

Beads (filed in the workspace `bd`):

- (A) `flext-vjj1s` — Parent: Pydantic governance program (this plan).
- (B) `flext-vjj1s.1` — flext-core facade exports (Phase 2 scope).
- (C) `flext-vjj1s.2` — Enforcement: ast-grep detection rules under
  `flext-infra/src/flext_infra/codemod/rules/` (precedent:
  `ban-ai-hub-crg-library-boundary.yml`) for the anti-catalog; assess adding enforcement
  catalog rows where runtime detection already exists.
- (D) `flext-vjj1s.3` — Automated migration: inventory via
  `commands/inspection/pydantic-boundary-audit`, then `make mod` (ast-grep + Rope + LSP)
  per repository. Known targets: `model_construct()` in
  `flext-infra/src/flext_infra/deps/toml_phase.py` and
  `flext-ldif/src/flext_ldif/_models/results.py`; diffuse `SkipValidation` uses (justify
  at owner or exterminate); any `ValidationError` catch that normalizes;
  `json.loads`+validate pairs; raw-base model declarations in consumers. Depends on (B)
  and (C).
- (E) `flext-vjj1s.4` — Superproject law pointers (Phase 3 scope).

Migration loop (per repository, one bead lane at a time): audit → detect (ast-grep) →
rewire (`make mod`) → gates → runtime proof → land on integration → retire lane.

## Phase 5 — mise.lock regime extermination

Bead: `flext-vjj1s.5`.

Artifacts:

1. ai-hub generator cutover on `fix/extinguish-mise-lock` (stops writing
   lockfile/locked, drops `mise lock --global --bump`, authenticates owned-release
   resolution via declared forge credentials + `gh auth token`).
2. Global `mise.lock` deletion (ai-hub owner side).
3. Fleet repo-level `mise.lock` deletions in flext members.
4. flext-infra `.mise.toml.j2` keeps the unlocked regime (explicit
   `settings lockfile=false` if needed); `.mise.toml` stays a generated projection owned
   by flext-infra + ai-hub global registry.

Evidence (partial — 2026-09-08, ~70%):

- [x] ai-hub generator cutover — landed on ai-hub `origin/dev` (`646975403` contained
      via PR merges); authenticated resolution live
- [x] Runtime regime — `lockfile = false` present, zero `locked`/`tool_config`, global
      `mise.lock` absent, `mise install` exit 0 ("all tools are installed"), cliproxy
      resolves `7.2.145-dc7` (newer than the dead lock)
- [x] agents repo lock — PR #127 merge `cf76d6f9` on `dev`; file removed
- [ ] Fleet member `mise.lock` deletions + `.mise.toml.j2` unlocked confirmation —
      REMAINING (next-actions queue item 2)

## Phase 6 — agents repo convergence with FLEXT

Bead: `flext-vjj1s.6`.

Artifacts:

1. Centralized Make control plane from flext-infra (selector-free verbs); map current
   homegrown verbs (setup/docs/audit/waza/static/conform/duplication/mod/shell/runtime)
   onto the fleet-standard surfaces and retire duplicates.
2. `.mise.toml` as a flext-infra-generated projection.
3. Minimal agent/profile changes.

Evidence (fill at completion):

- [ ] Gates — exit:
- [ ] Runtime proof — exit:
- [ ] Propagation — SHA:

## Propagation protocol (every phase)

1. All gates green in the phase worktree; runtime proof recorded above.
2. Absorb integration base (`git merge --no-ff`), resolve hunk by hunk.
3. Merge commit (never squash/rebase) onto the declared integration branch.
4. Fast-forward push; record SHA; retire the lane worktree after ancestry proof against
   a just-fetched base.

## Change log

- 2026-09-08: Plan created from approved v3 scope (operator request).
- 2026-09-08 (post-landing): Phases 0–3 DONE and active in runtime (`9e3d1628d`,
  `f751d6029`, `c11ffa08`+`cf76d6f9`, ai-hub dev); beads `.1`/`.4` closed; status
  dashboard and next-actions queue added; Phase 5 at ~70%; remaining core = `.2`
  enforcement then `.3` migration; `.6` convergence epic open.
