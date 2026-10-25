---
description: Use root Make, structural codemods, CRG, and LSP as the operational surface
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-01","route:both"]'
---

# Use selector-free root Make verbs

Before the first effect, resolve commands and practices from that repository's
AGENTS.md, README, docs and selected skills. Verify unknown commands, flags,
signatures or practices against declared docs, source or native help; otherwise
do not execute them. Success without canonical authority is still a defect.

Governed first-party projects follow this lifecycle; third-party forks follow
upstream, not another project's private control plane. Source inspection, native
help and selected Git/tracker/coordination APIs are preflight/control operations,
not gate substitutes. A broken Make gate never authorizes another tool or CLI to
obtain green.

Diagnostics, validation, generation, formatting, correction, tests, Waza, builds,
publication, deployment, and maintenance execute only through one explicit verb in the
repository root Makefile. No Make selector, underlying-tool argument,
environment-dispatched sub-operation, file/match filter, inline Python, raw tool,
private module, wrapper, alias, or compatibility entry point is an operational
substitute. A parameter explicitly declared by a verb's native help belongs to that
verb; it never authorizes an undeclared filter or a retired command.

Invoke each verb directly to perform its declared operation. Do not introduce an apply
selector, acknowledgement flag, or hidden execution mode. A distinct operation receives
a distinct public root verb; a missing verb is repaired at the Make/codegen owner before
work continues.

### Bounded FLEXT native-bootstrap route

For the explicitly selected `flext-0029c` native-environment-bootstrap task only,
use direct public `flext-infra` operations for diagnosis, runtime, refactoring and
gates; Make integration is last, coordinated with `flext-itpd1.4.13`. This bounded
route supersedes this rule's Make-only routing, not operation ownership, native
failure propagation, deadlines or evidence requirements. The branch-matched FLEXT
execution-context and ADR-010 own its confirmed provisioning/import trust boundary.
No raw tool, private worker, alternate producer or installed governance edit is
authorized. Documentation aligns before code; repeated native QA after causal
repairs and convergence checks is permitted, with tests changed only after real
subsystem and cold-bootstrap proof. No unchanged retry or hidden lifecycle
delegation is permitted; source alignment alone proves no runtime or delivery.

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

A verb may validate its own required inputs and the integrity of its own output.
That does not authorize another operation: formatting and repair do not rerun checks;
generation and structural transformation do not invoke the quality battery; setup,
upgrades and tests do not invoke generation or conformance. Setup consumes an existing
lock; upgrade does not install its result. A missing cold-start input is corrected
through its explicit owner, never by silently adding the missing operation to another
verb.

A declared composite lifecycle has its own public verb and a documented sequence.
It never changes the meaning of these atomic verbs. Validation of a refactoring invokes
the required verbs explicitly and records each result once; repeated generation, lock
resolution or checking hidden inside that sequence is a defect.

Every command inventory honors the repository `.gitignore` through the shared Git-aware
owner. It does not disable language caches, delete ignored caches in ordinary flows,
bypass standard ignores, or maintain a parallel artifact list.

Before a non-trivial refactor, use the repository's declared structural capabilities.
Repeated wiring changes execute through `make mod` and tested ast-grep rules; manual
file-by-file rewiring is forbidden. When the host runtime has selected CRG or LSP, its
public command/hook/MCP resolves symbols, relationships, consumers, definitions, and
references. A portable library must not import that host, produce its index, or fail
merely because the optional runtime is absent. An available selected runtime that fails,
an absent `mod` verb, failed codemod test, unexpected match cardinality, or
non-idempotent rewrite is RED and is corrected at its owner without a manual fallback.

The indexed tool's host owns initial build, incremental update, storage and readiness.
Directories, empty databases and failed-initialization artifacts prove no usable
index. Consumers query public readiness, not private artifacts. Never retry update
as build, create placeholder state or normalize an incomplete index.

The first command failure and raw traceback propagate. Warning, skip, empty output,
missing tool/report, partial execution, retry, normalization, or a successful wrapper
around a failed child is RED.

Test applicability and the explicit FLEXT connectivity prerequisite exception
have one owner: `rules/testing/observable-runtime.md`. Preserve its unexecuted
node identities and dispositions. An authorized prerequisite skip never proves
connectivity, complete behavioral validation or production readiness; a runner
that promotes it to any such success must be repaired.

Read-only predicates retain their documented native status, schema and decisive
result. False is neither gate success nor permission for dependent effects.
Unknown nonzero exits and error text never become absence; missing gate evidence
is RED. The diagnostic owner classifies emitted diagnostics; quoted input words
are not emitted diagnostics.

## Command deadline and performance

Invoke every command with a maximum wall-clock duration of 120 seconds, including
activation, preflight, lock acquisition, subprocesses and termination. This requirement
also applies to setup, complete test suites and profiling. A deadline wrapper is
required when the native entrypoint does not already enforce that bound. It does not
replace the declared operation, change its scope, suppress output or turn a failure
into success.

Reserve termination time inside the bound: request termination no later than 118
seconds and finish terminating owned children by 120 seconds. Nested operations consume
the remaining invocation budget, never a fresh budget per child. Do not signal another
actor's process or remove its lock to obtain the window.

A timeout is an incomplete failed invocation. Preserve its native output, exit,
completed scope and available profile. Before another invocation, identify and correct
the measured cause; do not retry unchanged, increase the limit, move the command into
an unbounded background job, or split its output into a false complete receipt.

For slow Python generation or migration, resolve the root Make operation and its
declared opt-in profiling setting before invoking cProfile through that operation.
A missing capture binding requires command-owner repair, not an invented profiling
target, restored alias or private-module invocation. Bind captures to source, runtime,
configuration and scope. Separate wall/cumulative time and parent waits/child work.
Reuse native capture and existing run-receipt owners, not a parallel metadata
framework. Never backfill an old capture with invented configuration. Invalid caller
edges block optimization; independent native thread/process ownership must cover the
elected worker scope. Unrecorded child captures never mean zero child CPU.
Correct one measured cause, revalidate public behavior and compare the same operation
before scaling. Reuse analysis owners, never a parallel cache/scanner/engine.
Native locked executable lookup consumes the configured tool request directly;
do not replace it with a reconstructed command-line version request. Repair an
invalid lookup at its command/template owner before repeating setup or upgrade;
never disable locked mode, parse a native lock or borrow a host executable.
When upgrading moving Mise requests, use native lock advancement (`lock --bump`),
not a plain lock refresh that retains the previous resolution. Setup remains a
locked installation and never advances a lock.
Gate placement and opt-in instrumentation follow
[`gate-budget.md`](gate-budget.md).

Under documentation-only authorization, correct the documentation and record the
exact code obligation for missing deadlines or broken generators; do not edit
excluded code or claim enforcement. This discipline does not imply unwrapped
recipes enforce it. Automation invokes native verbs through the declared deadline
runner; workflow source proves that binding.

## Test verbs

This is the single semantic test contract. Repository catalogs own grammar, population,
selection mode and execution contexts. ADR-0031 and ag-wibx.1 supersede the fixed mapping
from `operator-ruling-2026-10-01-testmon-make-test-only`, not historical receipts.

- The selected repository's native Make catalog owns its test-operation name and
  inputs. Resolve them through its help before execution; never infer a removed
  entry from historical instructions or create a compatibility alias.
- Each operation executes its declared population and selection mode, without a
  hidden incremental pre-run, automatic full rerun or mode switch.
- Where pytest-testmon is declared, preserve its persistent database at its owned
  location under `rules/storage.md`; never delete or replace it to obtain a result.
- CI and pre-push invoke only their declared operation and preserve its database.
- Pre-commit runs no tests.
- A complete-suite operation executes the complete applicable nonempty inventory
  once and preserves its database. The catalog owns where it runs; an interrupted
  run or preceding incremental phase is not complete-suite evidence.
- Zero execution is acceptable only for an explicitly declared incremental operation
  with the integrity-checked typed cache hit of AGENTS.md law 14, never as tests passed.
- A single-file operation is permitted only when the selected catalog declares it
  and its typed repository-relative input. A whole-suite-only catalog permits no
  file/match filtering. This rule does not add operations absent from the owner.
- Raw pytest, undeclared file/match selection and database deletion/replacement are
  prohibited; no focused, full or CI route bypasses the declared operations.

The repository command owner implements this contract. A template, runner or workflow
that still runs tests at pre-commit, changes this selection contract or removes the
deadline is nonconforming; its presence does not create another permitted workflow.

## Zero-violation code gate

This section is the single declaration of the zero-violation code gate (operator
order 2026-10-03). Every other rule, skill, command, agent profile, and doc
references it and never restates it.

- New code is accepted only after `make mod` passes.
- A change is never closed while `make fmt`, `make fix`, `make check`, `make mod`,
  or the spelling gate reports any violation. The spelling gate is whichever of
  `make spell` and `make spells` the repository `make help` lists.
