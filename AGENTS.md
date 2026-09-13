<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law — Strict Prelude

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
    repository root Makefile. `APPLY=Y` is mandatory for `fix`, `fmt`, `check`,
    and every test verb. A full suite has its own verb, first runs the
    incremental verb, and uses the same persistent external testmon database.
14. Red means red: a warning, skip, empty output, missing tool, missing report,
    zero collection, caught exception, retry, or normalized failure is RED. The
    only acceptable zero-execution test result is a typed incremental testmon
    cache hit with an integrity-checked database and complete deselection
    accounting; it is never reported as tests passed. The first exception and
    raw traceback escape unchanged.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# AGENTS.md — agents

> Packaged governance `agents-governance` `0.3.0` owns the capability indexes: 62 agents, 50 rules, 102 skills. Consume them through `GovernanceBundle`; do not copy their bodies here.

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
This repository is the single writable authority for provider-neutral rules,
skills, commands, agent profiles, and their semantic evaluation resources. It
publishes the read-only `agents-governance` package. AI Hub alone discovers
projects, adapts providers, generates hooks and instruction artifacts, deploys,
and reconciles runtime state.

## Public contract

- `from agents_governance import GovernanceBundle` is the supported API.
- `GovernanceBundle.load()` loads packaged resources; an explicit physical root
  is accepted for source validation.
- Loading validates the complete catalog, semantic skill evaluations, approval
  lineage, governance ownership map, metadata, agent profiles, commands, rules,
  and strict prelude before returning one frozen snapshot.
- This package has no CLI, daemon, hook, publisher, projector, sync, cleanup,
  provider-home writer, fallback loader, or compatibility API.
- Consumer delivery is a transaction owned by AI Hub. A consumer may transform
  bundle records but may never edit this source or treat generated output as an
  authority.

## Repository development

Read [README.md](README.md), [rules](rules), [skills](skills), and
[ADRs](docs/adr/README.md) before mutation. Use only selector-free root Make
verbs and run `make setup APPLY=Y` before development gates. `setup`, `fix`,
`fmt`, `check`, and every test verb require exactly `APPLY=Y`; raw-tool and
inline substitutes are prohibited.

Prove changed behavior through the public bundle load before adapting tests.
Every Python test invocation, including focused, full, and CI, must keep the
same external persistent testmon database active. The public full verb first
runs incremental selection, then uses testmon's official no-selection mode; it
never bypasses or clears the cache. Tests exercise public roots with typed
fixtures and no mocks, monkeypatching, private imports, or hardcoded owner
values. Warning, skip, empty output, missing tool/report, or zero collection is
RED. Zero execution is acceptable only for a typed incremental testmon cache
hit with an integrity-checked database and complete deselection accounting, and
must never be reported as tests passed.

Generated files carry an owner and exact regeneration instruction. Change their
source, regenerate through the declared Make owner, prove a zero-change second
generation, rewire all consumers, and delete the old code, test, fixture,
document, alias, backup, and archive in the same cutover.

## FLEXT project law

For `internal_flext`, apply the complete strict contract in the
`flext-development` skill and `rules/architecture/internal-clean-architecture.md`.
The structural MRO is `c → t → p → m → u`; operational facades are `r`, `e`,
`x`, `h`, `d`, and `s`. Each family lives under `_<module>/`, starts with
`base.py`, and is composed by explicit inheritance. Public `api.py` is the only
composition root and `cli.py` is a thin adapter. Modules have at most 200
logical lines and one top-level class; declarations are pure. Boundary input
and output use Pydantic 2, type aliases live only in `t`, protocols only in `p`,
and contracts never use `Any`, `object`, `Optional`, or `dict`. Domain and
application layers import no I/O, adapter, or framework. Local aliases,
redeclared owner values, concrete service dependencies, parallel facades, and
handwritten generated roots are blocking violations. `third_party_fork` retains
its upstream architecture.

## Lifecycle

Gas City owns workspace placement for this repository; `gc status` is the
effective-state authority (declared default plus runtime override). While the
city or this rig is suspended, work only in this existing checkout, invoke no
Gas City or Beads mutation, and create no substitute ledger.
Stop at `dev` unless the operator explicitly authorizes promotion. No increment
is DONE without required gates, reviewed merge-commit landing, post-merge public
runtime proof, and canonical tracker closure.

## Operator cycle lessons

- **Fix-forward permanente:** never rebase, force-push, or cherry-pick an
  authorized lane. Integrate the base with `git merge --no-ff`, revalidate the
  combined state, then land.
- **Pouso:** landing requires real validation (command + exit code + output),
  zero warnings, and record on the integration branch at cycle end. A rejected
  FF-push means `git merge --no-ff` the base into the lane.
- **Coordenação:** the orchestrator runs parallel subagents per file owner. An
  empty subagent result is not a claim — verify by diff before accepting.
- **Resíduo zero:** untracked `.bak`/backup artifacts are defects, never carry-over.
- **Gate bare:** a CI check invoked without the project environment must be
  stdlib-only at its script owner; provisioning env in the workflow is a
  workaround, not a fix. Prove the gate by running it exactly as CI does.
- **Subagentes rápidos:** dispatch independent research/verification/
  bookkeeping to fast parallel subagents; the main thread alone owns sequenced
  effects (merge, land, bead closure with merge evidence).
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->
