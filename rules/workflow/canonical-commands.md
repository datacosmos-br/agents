---
description: Use root Make, structural codemods, CRG, and LSP as the operational surface
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-01","route:both"]'
---

# Use selector-free root Make verbs

Before effects, resolve commands/practices from repository AGENTS.md, README,
docs and selected skills. Verify unknown commands, flags and signatures against
declared docs, source or native help before execution.

First-party projects follow this lifecycle; third-party forks follow upstream.
Source inspection, native help and selected Git/tracker/coordination APIs are
preflight/control, never gate substitutes. A broken Make gate authorizes no
replacement tool or CLI to obtain green.

Diagnostics, validation, generation, formatting, correction, tests, Waza, builds,
publication, deployment and maintenance require explicit root Make verbs. No selector,
underlying-tool argument, environment dispatch, file/match filter, inline Python, raw
tool, private module, wrapper, alias or compatibility substitute. Native-help
parameters belong to their verb, not undeclared filters or retired commands.

Repair missing verbs at the Make/codegen owner; no acknowledgement flag or hidden
mode substitutes.

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

Each verb owns only its declared operation, including prerequisites, hooks,
recursive Make, wrappers and callbacks:

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

Composite lifecycles require a public verb, documented sequence and atomic semantics.
Invoke and record required refactoring-validation verbs once; hidden repeated
generation, lock resolution or checks are defects.

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
directories, empty databases and failed initialization prove no index. Never retry
update as build, create placeholders or normalize incomplete state.

Apply [strict execution](../runtime/strict-execution.md) and
[observable outcomes](../testing/observable-runtime.md): preserve first failure and
raw traceback; wrappers never turn failed children green.

Test applicability, FLEXT connectivity prerequisites and their non-success
dispositions follow [observable-runtime](../testing/observable-runtime.md#host-services-and-capability-gating-operator-decisions-2026-09-29).
Preserve unexecuted node identities; repair runners that promote them to acceptance.

Read-only predicates preserve native status, schema and decisive result. False
permits no dependent effect and proves no gate success. Unknown nonzero/error text is
not absence; missing evidence is RED. Classify diagnostics, not quoted input words,
at their emitting owner.

## Command deadline and performance

Every command, including setup, full suites and profiling, has a 120-second bound
covering activation, preflight, locks, children and termination. Wrap unenforced
entrypoints without changing operation/scope, suppressing output or normalizing failure.

Use the Make owner's native deadline runner. Where enforcement is absent, the
external form is `timeout --signal=TERM --kill-after=<reserve>s <work-budget>s make <verb>`;
work budget plus termination reserve must fit the declared total bound. Shared locks
use bounded `flock -w <seconds>`. Resolve both values from the selected owner, never
freeze a sibling's reserve or add a second budget (operator order 2026-10-24, tracker memory
`operator-order-2026-10-24-make-always-with-timeout`).

Reserve termination time inside the 120-second total bound: TERM begins no later than
total minus reserve, and all owned children terminate within that total. Nested
operations consume the remaining invocation budget,
never a fresh child budget. Do not signal another actor's process or remove its lock
to obtain the window.

Timeouts are incomplete failures. Preserve output, exit, completed scope and profile.
Repair the measured cause before repeating; no unchanged retry, higher limit,
unbounded background job, idle slow-run queue or complete receipt from partial outputs.

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

Workflow source proves deadline-runner binding; unwrapped recipes prove no enforcement.
Documentation-only work records gaps without editing excluded code or claiming implementation.

## Test verbs

This contract supersedes `operator-ruling-2026-10-01-testmon-make-test-only`'s fixed
mapping (ADR-0031, ag-wibx.1), preserving historical receipts. Repository catalogs
own grammar, population, selection and contexts.

- Resolve test names/inputs through native Make help; no historical entry or alias.
- Execute the declared population and selection only: no hidden incremental pre-run,
  full rerun or mode switch.
- Preserve declared pytest-testmon databases at their `rules/storage.md` location;
  never delete or replace them for a result. CI/pre-push use their declared operation
  and database; pre-commit runs no tests.
- Use persistent incremental pytest-testmon for ordinary changes. Global coverage
  requires population, source identity and measured report; subsets/cache hits prove
  no global result. Collection follows `gate-budget.md`'s explicit target.
- Complete-suite operations execute the applicable nonempty inventory once,
  preserving the database in catalog-declared contexts. Interrupted or preceding
  incremental runs prove no complete suite.
- A declared full operation without Testmon loads no Testmon plugin and neither
  reads, leases nor writes its database; preserve it for incremental operations.
  The 2026-10-28 clarification keeps names in project catalogs, never a universal
  alias list. Admission, applicability, failures and deadline remain binding.
- Zero execution follows `AGENTS.md` law 14: an integrity-checked
  incremental cache hit, never tests passed.
- Single-file operations require catalog declaration and typed repository-relative
  input; whole-suite-only catalogs permit no file/match filters. This rule adds no verb.

Repair violating templates/runners/workflows; they authorize no alternative.

## Zero-violation code gate

Zero-violation gate owner (operator order 2026-10-03); other artifacts reference it.

- New code is accepted only after `make mod` passes.
- A change is never closed while `make fmt`, `make fix`, `make check`, `make mod`,
  or the spelling gate reports any violation. The spelling gate is whichever of
  `make spell` and `make spells` the repository `make help` lists.
