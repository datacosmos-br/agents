---
description: Use root Make, structural codemods, CRG, and LSP as the operational surface
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-01","route:both"]'
---

# Use selector-free root Make verbs

Before effects, resolve commands/practices from repository AGENTS.md, README,
docs and selected skills. Unknown commands, flags and signatures require declared
docs/source/native-help verification before execution.

Governed first-party projects follow this lifecycle; third-party forks follow upstream,
not another project's private control plane. Source inspection, native help and
selected Git/tracker/coordination APIs are preflight/control, never gate substitutes.
A broken Make gate never authorizes another tool or CLI to obtain green.

Diagnostics, validation, generation, formatting, correction, tests, Waza, builds,
publication, deployment and maintenance require explicit root Make verbs. No selector,
underlying-tool argument, environment dispatch, file/match filter, inline Python, raw
tool, private module, wrapper, alias or compatibility substitute. Native-help
parameters belong to their verb, not undeclared filters or retired commands.

Invoke directly: no apply selectors, acknowledgement flags or hidden modes.
Distinct operations require distinct public root verbs; repair missing verbs at
the Make/codegen owner first.

### Bounded FLEXT native-bootstrap route

Only selected bootstrap task `flext-0029c` uses direct public `flext-infra` for
diagnosis, runtime, refactoring and gates; Make integration is last, coordinated
with `flext-itpd1.4.13`. Preserve ownership, failure propagation, deadlines and
evidence. Branch-matched FLEXT execution-context/ADR-010 own the provisioning/import
trust boundary. No raw tool, private worker, alternate producer or installed governance edit.
Docs precede code; causal repair QA and convergence may repeat.
Tests follow subsystem and cold-bootstrap proof.
No unchanged retry, hidden lifecycle or source-only delivery claim.

## Operation ownership

Each public verb performs only its declared operation, transitively through
prerequisites, hooks, recursive Make, wrappers and library callbacks:

| Operation | Owned effect |
| --- | --- |
| `setup` | Install/activate declared locked environment/tools |
| `upg` | Resolve dependency/tool upgrades; write their locks |
| `gen` | Generate declared projections from authoritative inputs |
| `mod` | Apply declared structural transformations |
| `fix` | Apply declared repairs |
| `fmt` | Apply declared formatting |
| `check` | Verify selected contract without mutation |
| Test verbs | Execute declared test population under the contract below |

Verbs validate input/output integrity, never invoke another operation:
formatting/repair never rerun checks; generation/mod never invoke quality batteries;
setup/upgrades/tests never invoke generation/conformance. Setup consumes locks;
upgrade does not install. Repair missing cold-start inputs through their explicit owner.

Composite lifecycles require their own public verb, documented sequence and atomic
semantics. Invoke and record each required refactoring-validation verb explicitly
once; hidden repeated generation, lock resolution or checks are defects.

Ownership is not execution permission. Effectful setup/upgrades/deployment/cleanup
require authorized targets/effects or authorized native owner-managed fixtures.
Otherwise leave proof open; never upgrade everything, guess permission or bypass guards.

Inventories use the shared Git-aware owner and `.gitignore`. Never disable language
caches, delete ignored caches in ordinary flows, bypass ignores or duplicate inventories.

Non-trivial refactors use repository-declared structural capabilities. Repeated
wiring runs through `make mod` and tested ast-grep rules, never manual per-file
rewiring. Selected host CRG/LSP public commands/hooks/MCP resolve symbols,
relationships, consumers, definitions and references. Portable libraries never
import that host, produce its index or fail merely for its absence.
Available selected runtime failure, missing `mod`, failed codemod tests, unexpected
match cardinality or non-idempotence are RED; repair at their owner, no manual fallback.

The indexed tool's host owns build/update/storage/readiness. Query public readiness;
directories, empty databases and failed initialization prove no index.
Never retry update as build, create placeholders or normalize incomplete state.

Propagate the first command failure and raw traceback. Warning, skip, empty output,
missing tool/report, partial execution, retry, normalization, or a successful wrapper
around a failed child is RED.

Test applicability and the explicit FLEXT connectivity prerequisite exception
have one owner: `rules/testing/observable-runtime.md`. Preserve its unexecuted
node identities and dispositions. An authorized prerequisite skip never proves
connectivity, complete behavioral validation or production readiness; a runner
that promotes it to any such success must be repaired.

Read-only predicates preserve native status, schema and decisive result. False
permits no dependent effect and proves no gate success. Unknown nonzero/error text is
not absence; missing evidence is RED. Classify diagnostics, not quoted input words,
at their emitting owner.

## Command deadline and performance

Every command, including setup, full suites and profiling, has a 120-second
wall-clock bound covering activation, preflight, locks, children and termination.
Wrap unenforced entrypoints without changing operation/scope, suppressing output
or normalizing failure.

Reserve termination time: request it by 118 seconds and finish terminating owned
children by 120 seconds. Nested operations consume the remaining invocation budget,
never a fresh child budget. Do not signal another actor's process or remove its lock
to obtain the window.

A timeout is incomplete failure. Preserve output, exit, completed scope and profile.
Correct its measured cause before repeating; no unchanged retry, higher limit,
unbounded background job or false complete receipt assembled from partial outputs.

Profile slow Python generation/migration through the root Make operation's declared
opt-in cProfile binding. Repair missing bindings at their owner; never invent targets,
aliases, private invocations or old capture configuration. Bind captures to source,
runtime, configuration and scope; separate wall/cumulative time and parent waits/child
work. Reuse native capture, receipt and analysis owners, never parallel
metadata/cache/scanner/engine machinery. Invalid caller edges block optimization;
native thread/process ownership must cover elected workers. Missing child captures
prove no zero CPU. Repair one measured cause, revalidate public behavior and compare
the same operation before scaling.
Native locked executable lookup consumes the configured tool request directly,
never a reconstructed command-line version request. Repair invalid lookups at
their command/template owner before repeating setup/upgrades. Never disable
locked mode, parse native locks or borrow host executables.
Upgrade moving Mise requests with native `lock --bump`, not plain refresh retaining
the previous resolution. Setup remains locked and never advances locks.
Gate placement and opt-in instrumentation follow
[`gate-budget.md`](gate-budget.md).

Documentation-only work records missing deadline/generator enforcement without editing
excluded code or claiming enforcement. Unwrapped recipes prove no deadline.
Automation binds native verbs to the declared deadline runner, evidenced in workflow source.

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
- A declared full operation without Testmon loads no Testmon plugin, performs no
  incremental pre-run and neither reads, leases nor writes its database. Preserve
  that cache for ordinary incremental operations. The explicit 2026-10-28
  clarification keeps operation names in project catalogs, not another universal
  alias list. Full execution
  retains admission, applicability, failure accounting and the active deadline.
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
