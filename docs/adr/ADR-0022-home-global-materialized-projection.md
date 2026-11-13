# ADR-0022 — Global home `~/.agents` as a versioned materialized projection

**Status:** Amended by ADR-0038 **Date:** 2026-09-18 **Scope:** `~/.agents`, the global
read surface managed by AI Hub (`docs/plans/20260918-handoff-repasse-consolidado.md`);
publication effects follow laws 8 and 11 of `rules/law.md`

## Context

`~/.agents` is today a **symlink to the source checkout** `/home/marlonsc/agents`. The
diagnosis of the distribution rework approved on 18/09 (section §6, F6) measured the risk:
`make gen` rewrites the user's live config inside the checkout; `git clean`/branch
switch in the source can delete the home; hooks from two owners (ai-hub x Gas City) coexist
in the same projected JSONs. Full separation (home as an ai-hub transaction) is
F6 of the rework and presupposes ai-hub F1–F3 — currently red. Meanwhile, all
catalog-side consumption (session-router, global skills, waza) resolves through `~/.agents` and is
exposed to this coupling.

Operator decision (2026-09-18, this campaign): the home stops being a symlink **in this
campaign** and becomes a **materialized global projection** — a universal read
fallback for all projects and agents — **managed by AI Hub**, no longer as an
alias of the checkout.

## Decision

1. **Universal read projection, single semantic source in the SDK.** `~/.agents` materializes the
   semantic catalog through the SDK public API `catalog_resources(bundle)`, not by
   copying the checkout or overriding the data root in the controller (`skills/`,
   `rules/`, `commands/`, `agents/`,
   `evals/`, `docs/adr/`, `docs/research/`, `docs/security/`, `AGENTS.md`,
   `README.md`, `metadata.json`) — and nothing else: no `.git/`, `.venv/`, `.beads/`,
   `.gc/`, `worktrees/`, `dist/`, checkout provider surfaces (`.claude/`,
   `.codex/`, `.cursor/`, `.gemini/`, `.opencode/`, `.kilo/`) nor live user
   config. The existing wheel `force-include` in `pyproject.toml` is the authority
   for enrolling the resources; `config/` and the enrollment document itself are
   private SDK inputs, not central publications. The sdist keeps the same
   enrolled sources. The API returns a path-ordered tuple of frozen
   records `CatalogResource(relative_path: str, content: bytes, mode: int,
   sha256: str)`, with physical relative paths, exact bytes, permissions and the
   SHA-256 digest of those bytes. Symbolic links and non-regular types fail; regular
   hardlinks keep per-path identities, as in the existing skills catalog.
   Skill resources keep the policy and digest of the already existing reader.
   Central `AGENTS.md` is composed of `bundle.law.prelude` and
   `render_capsule(bundle).text`, by the existing semantic owners, without the
   repository's local scope block or AI Hub repository instructions.
   Legacy `UNIVERSAL_CORE.md` is not enrolled automatically: an old relinker
   does not create catalog authority. `AGENTS.md` enters by measured consumer: it is a
   declared target of
   `ssot_relink` and of the ai-hub fail-closed gate `projection_identity_gate`
   (`config/governance.yaml:10-16`). Consumers read; no consumer writes —
   a consumer write into the home is a reported defect, not an accepted state.
   This boundary declares the source protocol; it does not attest publication or execution.
   Equality of bytes, modes and digests between source and installed distributions requires
   separate native proof, as does effective transactional consumption by AI Hub.
   Adoption of this API by the AI Hub runtime is not proven by the SDK source
   change; the consumers cited above describe the historical motivation.
2. **Version stamp + digest (P5/ADR-0015).** The home carries
   `.agents-governance.json` with `owner`, bundle version, `generated_at` and per-tree
   digests. Convergence is decided by version+digest, never by blind byte-diff.
3. **Management belongs to AI Hub (amendment G0).** The only sanctioned tool to
   materialize/verify the home is the **ai-hub** deploy transaction (the
   catalog-home surface of F6 of the distribution rework). **The agents repo carries no
   tool, Make verbs or home gate** — it is a pure read-only catalog
   (ADR-0008); the original clause that created `tools/home_projection.py` +
   `home-sync`/`home-check` is **REVOKED** (it created a distribution mechanism
   parallel to ai-hub).
4. **Transitional state (until ai-hub takes over):** static copy materialized on
   18/09 (symlink backup in `~/.agents-archive/home-desymlink-2026-09-18/`),
   with a manifest already in ai-hub format; stale risk documented; the stale repair
   is ai-hub management taking over — **never restore the symlink**.
5. **Transition with backup.** Symlink removal preceded by a dated tar backup +
   MANIFEST (doctrine: deletion outside git only with backup). The repair of any
   post-transition failure is forward (ai-hub management), never symlink restoration.

## Consequences

- The source checkout stops being a single point of failure for the home: `git clean`/branch
  switch no longer touch what consumers read.
- The checkout's `make gen` goes back to writing only the checkout's own surfaces; the
  user's live config (Gas City x ai-hub hooks) leaves the side-effect radius.
- Catalog x home drift becomes visible when ai-hub takes over verification
  (`projection_identity_gate` already fail-closed); in the interim, the staleness is known and
  accepted as a declared transitional state.
- Final transactional management belongs to ai-hub (F6 of the rework); the boundary
  **flext ⊄ private / private ⊇ flext** remains: nothing here creates a dependency of
  flext on agents/ai-hub.

## Amendment 2026-10-28 — minimum authenticated publication effects

Authority: the operator's joint-runtime plan requires minimum declarative changes,
preservation of existing native configuration and one existing publication owner.
Execution is recorded by `ag-wibx.2.1.1`, linked to the AI Hub delivery item
`aihub-6sls5.1`. This amendment declares the contract; it does not attest installed
propagation.

The SDK remains a read-only semantic catalog. AI Hub retains destination selection,
native-format adaptation, ownership verification, staging, publication and activation.
Reading current destination bytes for preservation and compare-and-swap checks does
not import that native configuration as semantic policy.

The publisher composes effects for each destination once and changes only the
declared owned artifact, field, entry or block. Preserve foreign/manual content and
syntax outside changed spans. A satisfied declaration produces no write, metadata
refresh or restart. Removal requires both declared scope and authenticated current
ownership; a glob, filename, missing marker or version mismatch alone grants no
authority to delete. Conflicting ownership or changed inputs fail before effects.

The owning rules are
[`atomic-effects`](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/runtime/atomic-effects.md) and
[`distribution-routing`](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/coordination/distribution-routing.md).
The conditional recovery procedure is
[`runtime-heal`](../../skills/domain/runtime-heal/references/procedure.md).
Provider eligibility and concrete native selectors remain consumer policy; they are
not copied into this package or inferred by an adapter.
