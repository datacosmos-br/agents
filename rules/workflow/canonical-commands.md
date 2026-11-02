---
description: Use root Make, structural codemods, CRG, and LSP as the operational surface
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-11-02","route:both"]'
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

Repair missing public verbs at the Make/codegen owner; no acknowledgement flags
or hidden modes substitute for them.

### Bounded FLEXT native-bootstrap route

Only selected bootstrap task `flext-0029c` uses direct public `flext-infra` for
diagnosis, runtime, refactoring and gates; Make integration is last, coordinated
with `flext-itpd1.4.13`. Scoped validation of a single change through an owner's
public scoped command follows "Scoped validation of one change" below, not this
bounded route. Preserve ownership, failure propagation, deadlines and
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

## Scoped validation of one change

A single change is validated and applied through its owner's scoped, parametrized
public command, never by a global or fleet-wide run (operator order 2026-11-02, tracker
memory `operator-rulings-2026-11-02-lint-gate-decisions`: no global `make` runs; one
rule at a time through the scoped CLI).

- The command is the one the selected owner's native help or docs declare, with its
  scope parameters (projects, rule identities, check mode) as part of that command: for
  example the FLEXT infrastructure owner's `refactor mod --projects <project>
  --rule-ids <rule> --check`. A declared scope parameter is not an undeclared filter.
- Fleet-wide verbs belong to the owner's declared closure and rollout gates, run once
  at their phase, never as the per-change validation loop and never repeated to
  discover what a scoped command already answers.
- A scoped command that is missing, ignores its scope or cannot run on a root
  (branch, worktree, member or external consumer) is a defect repaired at its owner;
  it never justifies the global verb, a raw tool, a wrapper or a private module.
- Deadline, first-failure propagation and evidence rules in this file apply unchanged
  to scoped commands.

## Command deadline and performance

Every command's deadline, profiling procedure and timeout outcome have one owner:
[command deadline](command-deadline.md).

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
