---
description: Use root Make, structural codemods, CRG, and LSP as the operational surface
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-01","route:both"]'
---

# Use selector-free root Make verbs

Before effects, resolve commands and practices from repository AGENTS.md, README,
docs and selected skills. Verify unknown commands, flags and signatures against
declared docs, source or native help; otherwise do not execute them.

Governed first-party projects follow this lifecycle; third-party forks follow
upstream, not another project's private control plane. Source inspection, native
help and selected Git/tracker/coordination APIs are preflight/control operations,
not gate substitutes. A broken Make gate never authorizes another tool or CLI to
obtain green.

Diagnostics, validation, generation, formatting, correction, tests, Waza, builds,
publication, deployment and maintenance use explicit root Make verbs only. No selector,
underlying-tool argument, environment dispatch, file/match filter, inline Python, raw
tool, private module, wrapper, alias or compatibility substitute. Native-help-declared
parameters belong to their verb, never authorize undeclared filters or retired commands.

Invoke verbs directly. No apply selector, acknowledgement flag or hidden mode.
Distinct operations need distinct public root verbs; repair missing verbs at the
Make/codegen owner before continuing.

### Bounded FLEXT native-bootstrap route

Only the selected `flext-0029c` bootstrap task uses direct public `flext-infra`
diagnosis, runtime, refactoring and gates; Make integration is last, coordinated
with `flext-itpd1.4.13`. Ownership, failure propagation, deadlines and evidence
remain mandatory. Branch-matched FLEXT execution-context and ADR-010 own the
provisioning/import trust boundary. No raw tool, private worker, alternate producer
or installed governance edit is authorized. Align docs before code; causal repair
QA and convergence may repeat. Change tests after subsystem and cold-bootstrap
proof. No unchanged retry, hidden lifecycle or delivery claim from source alone.

## Operation ownership

Each public verb performs only its declared operation. This applies transitively to
prerequisites, hooks, recursive Make calls, wrappers and library callbacks:

| Operation | Owned effect |
| --- | --- |
| `setup` | Install and activate the declared locked environment and tools |
| `upg` | Resolve dependency and tool upgrades and write their locks |
| `gen` | Generate the declared projections from authoritative inputs |
| `mod` | Apply declared structural transformations |
| `fix` | Apply declared repairs |
| `fmt` | Apply declared formatting |
| `check` | Verify the selected contract without mutation |
| Test verbs | Execute their declared test population under the test contract below |

A verb validates its inputs and output integrity, without invoking another operation:
formatting/repair do not rerun checks; generation/mod do not invoke quality batteries;
setup/upgrades/tests do not invoke generation or conformance. Setup consumes locks;
upgrade does not install. Repair missing cold-start inputs through their explicit owner.

A composite lifecycle has its own public verb and documented sequence, preserving atomic
semantics. Refactoring validation invokes each required verb explicitly and records it
once; hidden repeated generation, lock resolution or checks are defects.

Ownership grants no execution permission. Effectful setup/upgrades/deployment/cleanup
require authorized targets/effects or authorized native owner-managed fixtures.
Otherwise proof stays open; never upgrade everything, guess permissions or bypass guards.

Inventories use the shared Git-aware owner and `.gitignore`. Never disable language
caches, delete ignored caches in ordinary flows, bypass ignores or duplicate inventories.

Before a non-trivial refactor, use the repository's declared structural capabilities.
Repeated wiring changes execute through `make mod` and tested ast-grep rules; manual
file-by-file rewiring is forbidden. When the host runtime has selected CRG or LSP, its
public command/hook/MCP resolves symbols, relationships, consumers, definitions, and
references. A portable library must not import that host, produce its index, or fail
merely because the optional runtime is absent. An available selected runtime that fails,
an absent `mod` verb, failed codemod test, unexpected match cardinality, or
non-idempotent rewrite is RED and is corrected at its owner without a manual fallback.

The indexed tool's host owns build, update, storage and readiness. Consumers query
public readiness; directories, empty databases and failed initialization prove no index.
Never retry update as build, create placeholders or normalize incomplete state.

The first command failure and raw traceback propagate. Warning, skip, empty output,
missing tool/report, partial execution, retry, normalization, or a successful wrapper
around a failed child is RED.

Test applicability and the explicit FLEXT connectivity prerequisite exception
have one owner: `rules/testing/observable-runtime.md`. Preserve its unexecuted
node identities and dispositions. An authorized prerequisite skip never proves
connectivity, complete behavioral validation or production readiness; a runner
that promotes it to any such success must be repaired.

Read-only predicates preserve native status, schema and decisive result. False permits
no dependent effect and proves no gate success. Unknown nonzero/error text is not
absence; missing evidence is RED. The diagnostic owner classifies emitted diagnostics,
not words quoted in inputs.

## Command deadline and performance

Every command, including setup, full suites and profiling, has a 120-second wall-clock
bound covering activation, preflight, locks, children and termination. Wrap entrypoints
lacking native enforcement without changing operation/scope, suppressing output or
normalizing failure.

Reserve termination time inside the bound: request termination no later than 118
seconds and finish terminating owned children by 120 seconds. Nested operations consume
the remaining invocation budget, never a fresh budget per child. Do not signal another
actor's process or remove its lock to obtain the window.

A timeout is incomplete failure. Preserve output, exit, completed scope and profile.
Correct its measured cause before repeating; no unchanged retry, higher limit,
unbounded background job or false complete receipt assembled from partial outputs.

Profile slow Python generation/migration through the root Make operation's declared
opt-in cProfile binding. Missing bindings require owner repair, never invented targets,
aliases or private invocation. Bind captures to source, runtime, configuration and
scope; separate wall/cumulative time and parent waits/child work. Reuse native capture,
receipt and analysis owners, never parallel metadata/cache/scanner/engine machinery.
Never invent old capture configuration. Invalid caller edges block optimization;
native thread/process ownership must cover elected workers. Missing child captures
prove no zero CPU. Repair one measured cause, revalidate public behavior and compare
the same operation before scaling.
Native locked executable lookup consumes the configured tool request directly;
do not replace it with a reconstructed command-line version request. Repair an
invalid lookup at its command/template owner before repeating setup or upgrade;
never disable locked mode, parse a native lock or borrow a host executable.
When upgrading moving Mise requests, use native lock advancement (`lock --bump`),
not a plain lock refresh that retains the previous resolution. Setup remains a
locked installation and never advances a lock.
Gate placement and opt-in instrumentation follow
[`gate-budget.md`](gate-budget.md).

Documentation-only scope records missing deadline/generator enforcement without editing
excluded code or claiming enforcement. Unwrapped recipes prove no deadline. Automation
binds native verbs to the declared deadline runner, evidenced in workflow source.

## Test verbs

This test contract supersedes the fixed mapping from
`operator-ruling-2026-10-01-testmon-make-test-only` (ADR-0031, ag-wibx.1), preserving
historical receipts. Repository catalogs own grammar, population, selection and contexts.

- Resolve test names/inputs through native Make help; no historical entry or alias.
- Execute the declared population and selection only: no hidden incremental pre-run,
  full rerun or mode switch.
- Preserve declared pytest-testmon databases at their `rules/storage.md` location;
  never delete or replace them for a result. CI/pre-push use their declared operation
  and database; pre-commit runs no tests.
- Ordinary changes use persistent incremental pytest-testmon, not full suites per
  change. Global coverage claims require population, source identity and measured
  report, never subset/cache-hit extrapolation. Collection uses `gate-budget.md`'s
  explicit target.
- Complete-suite operations execute the whole applicable nonempty inventory once,
  preserving the database in catalog-declared contexts. Interrupted or preceding
  incremental runs are not complete-suite evidence.
- Zero execution is acceptable only for an explicitly declared incremental operation
  with the integrity-checked typed cache hit of AGENTS.md law 14, never as tests passed.
- Single-file operations require catalog declaration and typed repository-relative
  input; whole-suite-only catalogs permit no file/match filters. This rule adds no verb.
- No raw pytest or undeclared selection; focused, full and CI routes obey this contract.

Repair violating templates/runners/workflows; they authorize no alternative.

## Zero-violation code gate

Zero-violation gate owner (operator order 2026-10-03); other artifacts reference it.

- New code is accepted only after `make mod` passes.
- A change is never closed while `make fmt`, `make fix`, `make check`, `make mod`,
  or the spelling gate reports any violation. The spelling gate is whichever of
  `make spell` and `make spells` the repository `make help` lists.
