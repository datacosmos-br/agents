# ADR-0008 — GovernanceBundle is the read-only semantic boundary

- **Status:** Accepted
- **Date:** 2026-09-03
- **Scope:** Package ownership, public API, validation, and delivery boundary
- **Supersedes:** The provider-projection, runtime CLI, and composed-delivery decisions
  formerly recorded by ADR-0003, ADR-0004, and ADR-0005

## Context

This repository owns reusable governance meaning. AI Hub owns discovery of managed
projects, project classification, provider capabilities, generated instructions, hooks,
daemons, deployment, reconciliation, and global runtime distribution. Keeping either
responsibility on both sides created two owners and let runtime projection, home writes,
cleanup, backup, and compatibility paths drift independently from deployment reality.

## Decision

The `agents-governance` distribution exposes one immutable public snapshot:

```python
from agents_governance import GovernanceBundle

bundle = GovernanceBundle.load()
```

`GovernanceBundle.load(root=None)` is read-only. The frozen result contains exactly
these public fields: `root`, `schema_version`, `distribution_version`, `config`,
`skills`, `skill_metadata`, `commands`, `agents`, `rules`, and `law`. Loading validates
the complete semantic catalog, approval lineage, ownership map, metadata,
provider-neutral skill evaluation resources, and strict law surface before returning.
The same resources are packaged in both wheel and source distribution, so installation
does not rely on this checkout.

This distribution has no executable, provider renderer, projector, publisher, hook or
daemon implementation, project discovery, home-directory operation,
sync/clean/backup/archive command, live model/scanner runner, compatibility alias, or
second load path. AI Hub consumes the public bundle and alone owns all adaptation and
effects. Provider-generated files identify that owner and the exact regeneration
command; they never become canonical input.

**Amendment — 2026-09-14:** removed the residual project-tree writer, its exclusive
workspace configuration, and the `gen`/`propagate` development routes. AI Hub already
consumes `GovernanceBundle`, not that local mirror. Existing projected trees are not
deleted by this source cutover; their owned retirement belongs to AI Hub. Complete skill
references, scripts, and evaluation resources remain part of the read-only package and
its distribution contract.

**Amendment — 2026-09-14 (resource contract):** each skill exposes its complete typed
resource inventory, with format, executable policy, configured mode and SHA-256.
`config/skills.json` owns that policy. `make runtime` compares installed sdist and wheel
resources against source bytes and declared modes through the public bundle. Development
gates include the executable Python resources and provision their SDKs without making
those SDKs package runtime dependencies. Claude and Poolside parser resources accept
authenticated private envelopes on stdin and emit complete structured evidence on
stdout; they neither discover physical sources nor publish files. AI Hub's adapter owns
authentication, association, private persistence and publication. Parser readiness does
not claim that downstream automatic collection is implemented.

**Amendment — 2026-09-14 (continuation context):** `strategic-compact` and
`plan-handoff` retain minimal owner/source revision, current refs, gate evidence,
freshness and next-action references on the existing authorized surface. They do not
create a second execution ledger or treat historical sessions as current authority; only
stale or unproven dependencies require renewed discovery.

The development surface is the standard Make vocabulary. Mutating correction targets
perform their declared operation directly. No selector is accepted.

**Amendment — 2026-09-14:** the operator removed Make application controls, including
the former dry-run override. Root verbs now have one execution contract without an
acknowledgement or replacement flag. Reconciliation is tracked by `flext-ro6mj.1`.

Every test run, including incremental, full, and CI runs, goes through a dedicated root
Make verb and the same external persistent pytest-testmon database. `make test-full`
first runs `make test`, then runs with both `--testmon` and `--testmon-noselect`; direct
or cache-bypassing pytest is invalid.

Runtime/public-contract proof precedes tests. Tests verify observable public behavior
and never define it; they use public roots, typed fixtures, and the applicable
flext-tests `tm/c/t/p/m/u` and conftest owners, with no mocks, private imports,
duplicated configuration, or hardcoded inventory totals.

FLEXT-managed projects preserve the strict dependency direction
`settings -> config -> c -> t -> p -> m -> u -> base -> services -> api -> cli`. They
keep one top-level class per module, move family members under `_<module>/` beginning
with `base.py`, and compose the public facade through an explicit diamond MRO.
flext-infra owns its validator, gates, and codegen; flext-core owns the reusable runtime
primitives.

## Consequences

- A consumer imports the distribution and receives one completely validated semantic
  snapshot or the first causal failure.
- Delivery can evolve in AI Hub without making provider details part of the semantic
  package contract.
- A cutover removes every old consumer, test, fixture, document, generated projection,
  backup, and archive in the same change. Old and new never coexist.
- Model-dependent evaluation and runtime validation remain AI Hub work; Waza here
  validates only the packaged provider-neutral skill resources.
