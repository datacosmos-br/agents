# FLEXT development procedure

## Establish the active owners

1. Work from the authorized physical repository and read its `AGENTS.md`,
   manifests, dependency graph, configuration, generator policy, Make surface,
   CI, tests, public consumers, and generated markers.
2. In a fleet, derive members and gitlinks from the active umbrella; treat each
   member as an independent repository. Historical branches, archives, other
   checkouts, provider homes, and generated outputs are evidence, never owners.
3. Elect the smallest current owner before editing. `flext-core` owns the runtime
   foundation; runtime consumers depend toward it. `flext-infra` owns reusable
   build, conform, code-generation, and policy machinery and is not a consumer
   runtime dependency. `flext-tests` owns reusable test fixtures and helpers.

Missing, branch-mismatched, external, or ambiguous ownership stops with zero
effects. Never resolve a missing owner from another checkout or a personal home.

## Resolve branch-matched law before FLEXT effects

The FLEXT root `AGENTS.md` and the branch-matched local `flext-law` skill
exposed by the FLEXT repository's provider skill tree (declared in the
repository's own `AGENTS.md`) are read from the exact branch or release the
active checkout is on. In standalone mode, with no parent workspace, read the
raw GitHub file pinned to that same branch or tag, never `main`. These compose
above the catalog's own global owners: `AGENTS.md`, `make-check`, and
`verification-loop`. Before any landing effect, use `pr-sheriff`: resolve the
workspace/account through the declared forge authority, collect fresh direct
forge evidence for the
declared integration branch and authorized head OID, then bind the merge to
that OID.
Missing or branch-mismatched authority fails the same as a missing owner
above: zero effects, no fallback to `main` or a same-named catalog entry.

## Preserve the architecture

- Use Python 3.13 and Pydantic 2 from the manifest. The strict dependency chain
  is `settings → config → c → t → p → m → u → base → services/*.py → api.py →
  cli.py`: typed `settings` own external input, typed `config` owns validated
  derivation, and the canonical structural facets follow in order — `c`
  constants, `t` types, `p` protocols, `m` models, `u` pure utilities. `base`
  contains only minimal shared foundations, `services/` owns use cases receiving
  `p` dependencies, `api.py` is the programmatic facade and composition root,
  and `cli.py` is a thin process adapter only for a declared CLI capability.
- `c/t/p/m/settings/config` never import `base`, `u`, `services`, `api`, or
  `cli`; `base/u` depend only inward; services depend on typed ports; API and CLI
  assemble the graph. Type-only reverse references stay under `TYPE_CHECKING`.
- Every module consumes the typed objects published by `settings`, `config`,
  and the facet namespaces directly through their owning imports. Redeclaring,
  local-aliasing, re-deriving, or copying owner-owned values into a leaf module
  is a violation: rewire the consumer to the owner instead.
- Use the `flext-core` container primitive only at the executable composition
  root. Business services receive dependencies explicitly and never resolve
  globals, string keys, shared containers, or introspected registrations.
- Keep one thin package API/MRO facade and one generated lazy package root. The
  facade module composes its entire `_<module>/*.py` family — starting at
  `base.py` — through explicit inheritance; the MRO is the facade. Do not
  create an eager export path, custom import router, compatibility alias,
  renamed service base, parallel namespace, or duplicate facade.
- Keep configuration and typed settings at the dependency foundation. Read their
  validated public namespaces; leaf modules do not reread environment or files.
- Represent project-owned structured boundary data with its declared Pydantic 2
  model and read-only protocol contracts. Validate once at ingress, preserve the
  typed object internally, and serialize once at true egress. Declaration layers
  remain data-only; behavior belongs to utilities, services, bases, APIs, or CLIs.
- Delegate generic process, serialization, schema, template, CLI, dependency-
  injection, and test machinery to their existing public FLEXT owners. Add no
  local substitute when an owner is missing or broken.

Project-specific namespace names, analyzer exceptions, package layouts, and
domain rules remain project-owned. Reproduce a tool diagnostic against the active
declared versions before changing its owner; never add a suppression or change
valid architecture merely to silence analysis.

## Enforce the single top-level class law

flext-core's enforcement catalog (`ENFORCE-001`, `ENFORCE-067`/`NS-000`) caps
every module at exactly one top-level class. An extra class is a violation
even where the mechanical detector stays green, because it skips
`_`-prefixed classes: a private module-level helper, an intermediate base
class introduced only to merge two base lists, a star-unpacked base tuple
(`class X(*BASES)`, which pyrefly rejects as invalid inheritance and erases
typing for every consumer), and a `TYPE_CHECKING`/runtime pair of the same
class all count. Extras become MRO mixins in their own module under the
facade tree (`_constants/_typings/_protocols/_models/_utilities`); every
public symbol nests inside its facade family, and the facade module imports
the family explicitly and composes it through that inheritance. A lazy
class-level attribute
uses the flext-core owner (`flext_core.lazy`, `lazy.attribute` /
`FlextLazyAttribute`), never a local descriptor; a heavy third-party import
defers inside the owning operation, never at module scope.

Finding any violation of this architecture — wrong layer order, a local
alias, a redeclared owner value, a second facade, a direct dependency
bypassing a typed port — is corrected at its owner by complete rewire and
revalidated through the full gate round in the same session; "pre-existing"
is never an exemption, and no violation is deferred.

## Change sources and migrate atomically

Treat `config/*.yaml`, schemas, typed settings, templates, and generator policy as
canonical where the repository declares them. Edit the owner, regenerate every
affected facet, root export, managed project section, Make/CI surface, and document,
then remove the superseded implementation and consumers in the same cutover.

Do not hand-edit generated files or create a second generation route. A broken or
missing canonical Make verb is repaired generically in its FLEXT owner and then
reused. Keep third-party forks and content-only repositories outside fleet mutation
unless the operator explicitly places them in scope.

A generated projection carries an explicit marker — `# @generated
AUTO-GENERATED FILE — Regenerate with: make gen`, a pyproject `[MANAGED]`
section, a generated Makefile, workflow, mise artifact, or lazy package
root — and is never hand-edited on that evidence alone. Change the
flext-infra template or generator, run `make gen WHAT=apply APPLY=Y` from
the workspace root, and prove `make gen WHAT=check` reaches a fixed point
before landing. Land the generator PR with flext-infra's own regenerated
projections committed in the same change; a generator PR that ships
template code without its own regenerated output fails flext-infra's own CI
on drift.

## Resolve the workspace lock and pinned toolchain

Inside a uv workspace, `uv lock --project <member>` always resolves and
writes the workspace root `uv.lock`; no flag scopes it to one member. A
member's own standalone `uv.lock` refreshes only from a standalone checkout,
through its own generated CI job. A member with no standalone lock resolves
`flext-infra` fresh from the integration branch in CI, so a flext-infra
template change turns every such member's `gen check` red until that member
regenerates and lands.

Treat the tool versions pinned in `uv.lock`/`pyproject`, not a stale
toolchain note, as the declared toolchain; every diagnostic from the locked
version is blocking. `make check WHAT=pyrefly PROJECT=<member>` is a
local-only gate: the hosted `CI=Y` run covers lint, pyright, security,
markdown, and smells, and a separate check-complement job runs the full
`make check` including pyrefly — a green top-level badge alone never proves
pyrefly passed.

## Validate and integrate

Run the real public import, facade, service, API, CLI, or generated consumer path.
Then run generation twice and require zero second-pass diff, followed by the
repository's formatter, lint, type, test, build, documentation, and integration
gates through the active root Make dispatcher.

Land fleet members on their declared integration lanes first. Prove each integrated
SHA, then update umbrella gitlinks, regenerate the root, and rerun combined gates.
The first runtime, child process, generator, fixed-point, or gate failure escapes
causally; no fallback, retry, partial publication, or success claim is valid.

Run only `make <verb> WHAT=<what> PROJECT=<member>` from the workspace root;
`make help` lists the verb catalog, and neither a bare `make val` nor a
`CHECK_GATES=` override exists. Land through one bead, one branch, one PR
against the declared integration branch, green native gates, the PR Sheriff
gate above, independent review or an operator-authorized administrative
merge, a merge commit (`gh pr merge --merge --match-head-commit <oid>`), a
refetch proving `git merge-base --is-ancestor` on the integrated SHA, bead
evidence, and branch cleanup. Coordinate concurrent lanes through a comment
on the owning bead, never a parallel ledger.
