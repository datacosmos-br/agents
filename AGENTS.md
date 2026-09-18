<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AIHUB Inviolable Law — Strict Prelude

1. Truth: never claim done/green/resolved without command, exit code, decisive output.
2. Root cause: exterminate bypass, fallback, shim, suppression, stub, hardcode, catch-based normalization, retry, compatibility, partial execution, keyring, or old+new coexistence.
3. Tracker first: use the canonical tracker only when selected and available. If its runtime is explicitly suspended, create no substitute tracker or ledger; preserve evidence in separately authorized Git/PR/CI and do not declare the phase DONE.
4. Research first: inspect code, docs, canonical sources before acting; never invent APIs, flags, facts, or behavior.
5. Owner first: use the project's declared facades/primitives; do not reimplement them locally.
6. Gate persistence: a failure stops only that invocation. Correct its owner,
   republish, and rerun until green; never switch phase or repository because a
   check, review, approval, or merge is pending. Escalate only after every
   authorized technical action is exhausted and the remaining condition is
   genuinely external or requires new authority.
7. Landing: native gates, commit, fast-forward push, bead evidence.
8. Divergence: FF push rejected → integrate by cooperation: `git merge --no-ff` the integration base into your lane, resolve conflicts, revalidate, land. Never rebase or force-push an authorized change or integration branch; adopt all current worktree state and fix it forward.
9. Escalation: impossible rule → exact error. Rule conflict → present both with numbers. Unclear → one targeted question. Never guess.
10. Precedence: NEWEST > OLDEST. USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default. Adjust lower/older to higher/newer. Doubt → ASK USER FIRST.
11. Workspace placement: follow the declared Gas City city/rig/Pack V2 contract in `rules/coordination/gascity.md`. While its runtime is suspended, operate only in the existing checkout and create no clone, worktree, city, rig, agent, formula, run, or session. Staging stays on the destination filesystem, never `/tmp`; backup and archive copies are prohibited.
12. Phase closure: keep the phase active through check repair, review resolution,
    independent approval, merge into the configured integration branch, and
    post-merge proof. Only then, with its Bead closed with evidence, is it DONE.
    When the operator states that no independent reviewer exists and authorizes
    an administrative merge, that authorization replaces the approval row alone;
    every other row stays mandatory and closure records the approval as
    operator-authorized, never as satisfied.
13. Root Make only: diagnostics, validation, generation, tests, Waza,
    publication, and deployment run only through selector-free verbs in the
    repository root Makefile; bare verbs perform their declared operation. A full
    suite has its own verb, first runs the incremental verb, and uses the same
    persistent external testmon database.
14. Red means red: a warning, skip, empty output, missing tool, missing report,
    zero collection, caught exception, retry, or normalized failure is RED. The
    only acceptable zero-execution test result is a typed incremental testmon
    cache hit with an integrity-checked database and complete deselection
    accounting; it is never reported as tests passed. The first exception and
    raw traceback escape unchanged.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

## AGENTS.md — agents

> Packaged governance `agents-governance` owns the capability indexes. Consume current
> inventories through `GovernanceBundle`; do not copy their counts or bodies here.

This repository is the single writable authority for provider-neutral rules, skills,
commands, agent profiles, and their semantic evaluation resources. It publishes the
read-only `agents-governance` package. AI Hub alone discovers projects, adapts
providers, generates hooks and instruction artifacts, deploys, and reconciles runtime
state.

### Public contract

- `from agents_governance import GovernanceBundle` is the supported API.
- `GovernanceBundle.load()` loads packaged resources; an explicit physical root is
  accepted for source validation.
- Loading validates the complete catalog, semantic skill evaluations, approval lineage,
  governance ownership map, metadata, agent profiles, commands, rules, and strict
  prelude before returning one frozen snapshot.
- This package has no CLI, daemon, hook, publisher, projector, sync, cleanup,
  provider-home writer, fallback loader, or compatibility API.
- Consumer delivery is a transaction owned by AI Hub. A consumer may transform bundle
  records but may never edit this source or treat generated output as an authority.

### Repository development

Read [README.md](README.md), the [rules index](docs/rules-index.md), [skills](skills),
and [ADRs](docs/adr/README.md) before mutation. Use only selector-free root Make verbs;
bare verbs perform their declared operation. Prove changed behavior through the public
bundle load before adapting tests.

### Lifecycle

Gas City owns workspace placement; `gc status` is the effective-state authority. While
the city or this rig is suspended, work only in this existing checkout, invoke no Gas
City or Beads mutation, and create no substitute ledger. Stop at `dev` unless the
operator explicitly authorizes promotion. No increment is DONE without required gates,
reviewed merge-commit landing, post-merge public runtime proof, and canonical tracker
closure.

### Authority map

Precedence: `rules/coordination/operator-precedence.md`.

By category:

- [Architecture](rules/architecture/) — clean architecture, DI, topology, ownership
- [Coordination](rules/coordination/) — lifecycle, beads, operator alignment,
  never-deduce, sessions
- [Ethics](rules/ethics/) — integrity, truth, and test-reality
- [Runtime](rules/runtime/) — execution, residue, environment, fail-fast
- [Workflow](rules/workflow/) — discovery, generation, documentation, gates
- [Security](rules/security/) — supply chain, scanners, prompt defense
- [Language](rules/language/) — runtime floor, authored language
- [Python](rules/python/) — config SSOT, Pydantic, typing
- [Flext](rules/flext/) — FLEXT-specific governance
- [Shell](rules/shell/) — bash guard rules
- [Git](rules/git/) — branch workflow, destructive guard, fork locality
- [Communication](rules/communication/) — caveman style

FLEXT architecture for `internal_flext`:
[`rules/architecture/internal-clean-architecture.md`](rules/architecture/internal-clean-architecture.md).
Operator mandate: [`VALIDATE_ON_CHANGE.md`](VALIDATE_ON_CHANGE.md).
