# FLEXT development procedure

## Establish owners before effects

1. Read the active repository's `AGENTS.md`, manifests, dependency graph,
   configuration, generator markers, root Makefile, public consumers, and
   current runtime identity.
2. In a fleet, derive members from the current umbrella. Each member is an
   independent repository; another checkout, branch, archive, provider home, or
   generated output is evidence, never an owner.
3. `flext-core` owns reusable runtime primitives. `flext-infra` owns validators,
   gates, templates, code generation, and fleet conformance. `flext-tests` owns
   reusable typed test machinery and the `tm/c/t/p/m/u` facets.
4. Resolve the branch-matched FLEXT law and current project profile. A missing,
   ambiguous, or mismatched owner stops before effects; never fall back to a
   protected branch or another checkout.

## Keep host automation outside portable libraries

The portable tooling package owns Git primitives and standalone Make, codegen,
and gate behavior. The selected host runtime owns live forge integration, code
graph indexes, language/refactor services, hooks, MCP, and automation daemons.
Static forge templates remain codegen data in the portable package; contacting
the forge or maintaining host analysis state does not.

A portable package may augment an operation through an installed host public
command, hook, or MCP capability. It never imports the host application, links
it as a language dependency, reads its private index, or reproduces its daemon.
If that runtime is absent and unselected, continue the complete standalone
operation without an error and without a substitute. If an available capability
is explicitly selected, propagate its first failure. The host daemon owns graph
build, incremental update, storage, and readiness; a managed project only
activates its workspace and queries the public runtime contract.

## Preserve Clean Architecture and strict DI

Apply `$py-dev` and its `$solid` parent before this FLEXT delta.

Domain and application import no I/O, adapters, frameworks, process state,
global registries, or concrete services. They depend on precise `p` ports.
Public `api.py` is the only composition root and injects concrete edges once;
`cli.py` is a thin process adapter over that API. Do not add service locators,
shared mutable containers, hidden singletons, string lookup, auto-registration,
or import-time wiring.

The structural facade MRO is `c → t → p → m → u`. Operational facades are `r`,
`e`, `x`, `h`, `d`, and `s`. Each family lives under `_<module>/`, begins with
`base.py`, and puts every additional class in its own module. The facade imports
that family explicitly and composes it through explicit inheritance. Do not
create tuple-unpacked bases, intermediate merge classes, parallel namespaces,
eager routers, compatibility facades, local descriptors, or a second API.

Every module contains exactly one top-level class and no more than 200 logical
lines. Declaration layers remain pure: `c` owns constants, `t` alone owns type
aliases, `p` alone owns protocols, `m` owns Pydantic 2 models, and `u` owns pure
utilities. All structured ingress and egress uses Pydantic 2. Public and DI
contracts use neither `Any`, `object`, `Optional`, nor `dict`; model values
precisely and express explicit null unions only where the domain allows them.
Model classes always extend an `m.*` preset, declarations resolve strictly
(never `model_rebuild`), and the complete Pydantic law — preset selection,
`p`/`r` contracts, conversions, validation, serialization, removal catalog —
is owned by `$pydantic-development`.

Settings own external input and config owns validated derivation before the
facade graph. Import and use their published objects directly. Never alias,
copy, redeclare, re-derive, or reread their values in leaf modules. Type-only
reverse references stay non-runtime and cannot mask a dependency cycle.

## FLEXT SOLID specialization

Reusable behavior belongs to the lowest existing public facet owner. General
dependency parsing, graph ordering, file discovery, and semantic operations live
on the appropriate `u` facade; a codemod, gate, service, API, or CLI consumes that
facade directly and owns only orchestration. Improve an existing utility with
typed keyword-only options and compatible defaults before considering another
method. Never add a domain-named utility wrapper, pass-through `_rules` method,
stateless discovery class, local alias, or adapter that only forwards to `u`.

For a cutover, inventory all imports and generated exports, rewire consumers to
the final facade, delete the adapter module, change the generator owner, and run
the root generation fixed point. A generated package root is evidence to
regenerate it, never a reason to retain the old class or edit the export by hand.

## Generate and migrate atomically

Edit only the declared configuration, schema, template, or typed source owner.
Run the selector-free root `gen` verb with `APPLY=Y`, regenerate every affected
facet/root/consumer, then repeat it and require zero change. A generated file
must state its writable owner, prohibit hand edits, and name its exact root Make
regeneration verb. flext-infra lands its own regenerated outputs with template
changes.

Rewire every consumer in the same cutover. Delete the superseded implementation,
test, fixture, document, alias, backup, archive, manifest entry, and generated
file immediately. A second generation route, missing root verb, partial fleet,
or old/new coexistence is RED and is corrected at flext-infra.

## Verify runtime, then tests, then integrate

Execute diagnostics, generation, formatting, correction, checks, Waza, tests,
build, publication, and deployment only through selector-free verbs in the
active repository's root Makefile. `fix`, `fmt`, `check`, and every test verb
require exactly `APPLY=Y`; every other mutation uses the same acknowledgement.
Repair a missing standard verb at the Make/codegen owner rather than invoking a
raw underlying tool.

First exercise the installed public import, facade, service, API, CLI, or
generated consumer. Only after runtime proof may tests run. Every test verb uses
the same external persistent pytest-testmon database. The public full verb first
runs incremental selection and then no-selection. Warning, skip, empty output,
missing tool/report, zero collection, catch, retry, or normalized failure is
RED. Zero execution is valid only for a typed incremental testmon cache hit with
database integrity and complete deselection accounting, and is never reported
as tests passed.

For `internal_flext`, construct tests only through flext-tests public facets and
shared conftest/typed fixtures. Use no mock, monkeypatch, private import, copied
configuration, or hardcoded owner value. Preserve the first exception, cause,
raw traceback, child status, and generated drift.

Land members on their declared integration lanes before updating umbrella
gitlinks. Publication, deployment, review resolution, and retirement also use
their explicit root Make verbs. Prove each integrated SHA and the post-merge
public runtime; never rebase, force-push, retry, archive residue, or report a
partial result as complete.
