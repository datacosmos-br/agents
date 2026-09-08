# Pydantic Governance Program — Living Plan

> Status: ACTIVE · Owner: operator request 2026-09-08 · Lane: `feat/pydantic-governance`
> This document is the execution reference base for the Pydantic governance
> documentation, skills, enforcement, and automated migration. Edit it in place
> at every phase boundary; record evidence under each phase before propagation.

## Goal

One canonical Pydantic 2 (project floor: declared dependency SSOT; workspace
installs 2.14.0b1, stable line 2.13.5) practice base for the fleet: how models
are declared in `m` with obligatory MRO presets, how protocols are declared in
`p`, how conversions from dict/TypedDict/dataclass/JSON are performed, how
validation and serialization are used, when read-only vs mutable vs strict base
models apply, how identity models (id/timestamps/version) are used, how typing
composes with `p` and `r`, how `settings` (runtime-adjustable) and `config`
(static rules) feed `c`/`t`/`p`/`m`/`u`, the complete good/bad practice
catalog — including the demonized `model_rebuild` (a strict fleet never needs
it) — and the automated migration that removes the bad practices from fleet
code.

## Discoveries (living)

- 2026-09-08: concurrent diet renamed skills to short slugs with
  `supersedes:` lineage (`python-development` → `py-dev`); Phase 1 edits
  target the current tracked names.
- Known violation pressure: the operator reports thousands of facade/MRO
  violations fleet-wide; enforcement (Phase 4, bead C) and the automated
  migration (bead D) are the response.
- 2026-09-08: mise root cause chain: the ai-hub generator
  (AiHubMiseConfigService) forced `lockfile=true` + `tool_config.locked=true`
  + `mise lock --global --bump` while its GitHub resolution was
  unauthenticated (403 rate limit), leaving a stale global lock that broke
  `mise install` fleet-wide; operator ordered extermination of the lock
  regime (fleet runs unlocked and current); fix branch
  `fix/extinguish-mise-lock`.
- 2026-09-08: execution model: main session acts as coordinator; bounded
  changes are dispatched to subagents; simple foreground edits continue in
  the main session.

## Phase 1 — Governance documents (`agents` repo, lane `feat/pydantic-governance`)

Artifacts:

1. `rules/python/pydantic.md` — distilled obligation rule (globs `**/*.py`).
2. `skills/technology/pydantic-development/SKILL.md` — router skill, extends
   `$python-development`, detects `pydantic`/`pydantic-settings`.
3. `skills/technology/pydantic-development/references/procedure.md` — the full
   reference: facade law, model MRO (obligatory), `p` protocol declaration
   (obligatory), preset decision table (read-only/mutable/strict), identity
   models (id/timestamps/version), inheritance and MRO rules, conversions
   (dict/TypedDict/dataclass/JSON), validation, serialization, `p`+`r` typing,
   performance, experimental policy, advanced types, anti-catalog, gates.
4. `skills/technology/python-development/SKILL.md` — compose
   `$pydantic-development` when the project declares Pydantic.
5. `skills/framework/flext-development/references/procedure.md` — Pydantic
   paragraph points at the new skill, presets, and TypeAdapter-once owners.
6. `commands/inspection/pydantic-boundary-audit.md` — read-only audit that
   inventories violations per repository and feeds Phase 4.
7. `evals/pydantic-development/` — suite + basic/edge/should-not-trigger tasks.

Evidence (fill at completion):

- [x] `make setup APPLY=Y` — exit: 0 (mise install unlocked + uv venv + sync;
      unblocked by the Phase 0 mise lock extermination)
- [x] `make fix APPLY=Y` / `make fmt APPLY=Y` — exit: 0 / 0 (24 files unchanged)
- [x] `make check APPLY=Y` — exit: 0 (GovernanceBundle.load: 121 skills incl.
      pydantic-development; waza: 121 suites, 0 MISS; installed wheel proof
      `ARTIFACT 0.4.0 … 121`)
- [x] `make test APPLY=Y` — exit: 0 (typed incremental testmon cache hit:
      4/4 deselected, integrity=ok, complete deselection accounting, warnings=0)
- [x] Runtime proof (bundle load / audit command load) — exit: 0 (check `audit`
      stage; command catalogued: 12 commands incl. pydantic-boundary-audit)
- [x] Propagation: merge commit onto `dev`, push — SHA: lane `2b51f60e`
      (merge commit SHA is the parent record on `dev`)

Phase 1 gate repairs adopted into this lane (pre-existing dev red, fixed at
root): three `skills/tool/*-session-extract`/`session-resume` frontmatters
migrated to the closed tag grammar v2 (dead `policy:*`/`provenance:*`/`tool:*`/
`updates:*` namespaces removed, `subject:agents` added).

## Phase 2 — flext-core facade exports (lane in `flext-core`)

Export the stable advanced declarations through `m` so the rule is executable
without direct imports: `StringConstraints`, `SerializeAsAny`, `FailFast`,
`Discriminator`, `InstanceOf`, `ValidateAs` (all present in the installed
floor). Facade exposure test through the public `m` surface.

Evidence (fill at completion):

- [ ] Runtime proof `from flext_core import m; m.StringConstraints` — exit:
- [ ] Gates (root dispatcher, selector-free) — exit:
- [ ] Propagation: FF push, merge commit onto integration, gitlink roll-up — SHA:

## Phase 3 — Superproject law pointers (lane in `flext`)

- Root `AGENTS.md` Conventions: one paragraph pointing at the skill, presets,
  and conversions owners.
- `.agents/skills/flext-law/SKILL.md`: Pydantic delta references the skill.
- Hunk-by-hunk adoption: `AGENTS.md` carries concurrent WIP; commit scoped
  hunks only.

Evidence (fill at completion):

- [ ] Gates — exit:
- [ ] Propagation — SHA:

## Phase 4 — Beads + automated migration

Beads (filed in the workspace `bd`):

- (A) `flext-vjj1s` — Parent: Pydantic governance program (this plan).
- (B) `flext-vjj1s.1` — flext-core facade exports (Phase 2 scope).
- (C) `flext-vjj1s.2` — Enforcement: ast-grep detection rules under
  `flext-infra/src/flext_infra/codemod/rules/` (precedent:
  `ban-ai-hub-crg-library-boundary.yml`) for the anti-catalog; assess adding
  enforcement catalog rows where runtime detection already exists.
- (D) `flext-vjj1s.3` — Automated migration: inventory via
  `commands/inspection/pydantic-boundary-audit`, then `make mod APPLY=Y`
  (ast-grep + Rope + LSP) per repository. Known targets: `model_construct()`
  in `flext-infra/src/flext_infra/deps/toml_phase.py` and
  `flext-ldif/src/flext_ldif/_models/results.py`; diffuse `SkipValidation`
  uses (justify at owner or exterminate); any `ValidationError` catch that
  normalizes; `json.loads`+validate pairs; raw-base model declarations in
  consumers. Depends on (B) and (C).
- (E) `flext-vjj1s.4` — Superproject law pointers (Phase 3 scope).

Migration loop (per repository, one bead lane at a time):
audit → detect (ast-grep) → rewire (`make mod APPLY=Y`) → gates → runtime
proof → land on integration → retire lane.

## Phase 5 — mise.lock regime extermination

Bead: `flext-vjj1s.5`.

Artifacts:

1. ai-hub generator cutover on `fix/extinguish-mise-lock` (stops writing
   lockfile/locked, drops `mise lock --global --bump`, authenticates
   owned-release resolution via declared forge credentials + `gh auth token`).
2. Global `mise.lock` deletion (ai-hub owner side).
3. Fleet repo-level `mise.lock` deletions in flext members.
4. flext-infra `.mise.toml.j2` keeps the unlocked regime (explicit
   `settings lockfile=false` if needed); `.mise.toml` stays a generated
   projection owned by flext-infra + ai-hub global registry.

Evidence (fill at completion):

- [ ] Gates — exit:
- [ ] Runtime proof — exit:
- [ ] Propagation — SHA:

## Phase 6 — agents repo convergence with FLEXT

Bead: `flext-vjj1s.6`.

Artifacts:

1. Centralized Make control plane from flext-infra (selector-free verbs);
   map current homegrown verbs
   (setup/docs/audit/waza/static/conform/duplication/mod/shell/runtime) onto
   the fleet-standard surfaces and retire duplicates.
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
4. Fast-forward push; record SHA; retire the lane worktree after ancestry
   proof against a just-fetched base.

## Change log

- 2026-09-08: Plan created from approved v3 scope (operator request).
