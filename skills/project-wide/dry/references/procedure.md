# Compact-code extermination procedure

## Non-negotiable outcome

Remove the maximum confirmed structural waste within the authorized affected
graph while delivering the complete requested behavior. Compactness is valid only
when a maintainer can still understand the control flow, public contracts remain
documented, and fresh runtime plus native gates prove the result.

Never optimize for raw line count. Dense expressions, implicit control flow,
metaprogramming, generic frameworks, premature helpers, broad base classes, or
utility dumping grounds can reduce lines while increasing semantic size. They are
failures, not DRY improvements.

## Flow contract

The canonical sequence lives in `search-first`; do not reproduce it here. Consume
its evidence packet, the current concept set from `yagni`, the authority map from
`ssot`, and the boundaries from `solid`. Activate once only for proven structural
waste spanning owners or callers; output the rewired graph for downstream
rechecks and final `simplify`. Re-enter discovery only when the owner, consumer,
dependency, or public contract truly changed.

## Research and baseline first

Apply `search-first` before editing. Resolve project instructions, architecture,
public entry points, authority candidates, generators, projections, dependencies,
callers, tests,
and native gates. Establish a green behavioral baseline through the real runtime;
if the baseline is red or missing, report the exact blocker instead of assuming
what must be preserved.

Measure the same scoped source set before and after the change. Prefer the
project's declared metrics facade; otherwise use `tokei` when it is installed.
Record languages, code, comments, blanks, and the exact exclusions. If Tokei is
required by the task but unavailable, fail loudly rather than inventing a counter
or installing tooling without authority.

Line counts reveal growth and duplication candidates; they do not prove quality.
Claims of runtime inefficiency require a representative profile, trace, benchmark,
query count, allocation count, or I/O count. Never infer speed from fewer lines.

## Build a semantic waste map

Trace behavior across definitions, callers, registrations, tests, configuration,
generators, and generated projections. Confirm candidates in these classes:

- duplicated rules, validation, transformations, queries, serialization, error
  mapping, configuration, or orchestration;
- repeated I/O, parsing, allocation, traversal, remote calls, or computation;
- dead branches, unused types, unreachable adapters, obsolete flags, and stale
  compatibility code with no dynamic or reflective consumer;
- long functions with multiple abstraction levels or unrelated reasons to change;
- god classes/modules that own domain policy, persistence, transport, formatting,
  state, and orchestration together;
- broad interfaces, helper bags, inheritance hierarchies, and indirection whose
  current consumers use only a narrow subset;
- comments or documentation that restate code while the actual public contract or
  non-obvious invariant remains undocumented.

Do not classify by size or textual similarity alone. Two similar blocks may encode
different policies; a large cohesive parser may have one responsibility; dynamic
registrations may make an apparently unreferenced symbol live. Read decisive
callers and runtime wiring before removing or merging anything.

## Exterminate at the owner

1. Protect public behavior, errors, ordering, side effects, security boundaries,
   and performance characteristics with focused tests or characterization.
2. Use the authority already selected by `ssot` for each duplicated piece of
   knowledge. Extend it and rewire all current consumers in the same change; do
   not select a different owner inside DRY.
3. Split god patterns by cohesive responsibility and real change reason. Keep a
   thin explicit orchestrator when sequencing is itself a responsibility; do not
   replace one god object with a god utility module or service locator.
4. Collapse needless layers, branches, wrappers, conversions, and repeated work.
   Reuse supported library primitives already pinned by the project.
5. Delete the obsolete implementation, dead paths, duplicate tests, compatibility
   surfaces, fixtures, flags, examples, and documentation. Old and new behavior
   must not coexist.
6. Apply `simplify` immediately to the coherent unit just changed. Keep names
   explicit and control flow readable. Extract an abstraction only when at least
   one real current consumer proves the shared semantic contract.
7. Recheck `yagni`, `ssot`, and `solid` after rewiring; remove any speculative
   layer, competing authority, and responsibility or dependency defect introduced
   by remediation.
8. Document public interfaces and non-obvious invariants at their owner. Remove
   commentary that merely narrates obvious code.

Every new line must be justified by a current acceptance criterion, invariant, or
maintainability boundary. A remediation that grows production code must explain
the unavoidable semantic value and prove that no smaller established owner can
deliver it; otherwise continue reducing.

## Verification matrix

Run the public runtime before general gates, after each architectural move that
invalidates evidence, and on the integrated result. Then run unit, integration,
static, type, build, security, generation, and projection fixed-point gates.

Repeat semantic searches for each removed owner and duplicated rule. Compare Tokei
on the identical scoped file set. When efficiency was claimed, repeat the same
profile or benchmark and report both measurements. Verify that:

- all required behavior and supported inputs remain present;
- causal errors still propagate loudly and no fallback was introduced;
- no duplicate owner, god utility, dead adapter, or unrewired consumer remains;
- complexity moved out of code only into an appropriate typed owner, never hidden
  in configuration, reflection, generated output, or documentation;
- public documentation and non-obvious invariants match runtime reality.

Report the SSOT authority used, consumers rewired, code deleted, Tokei
before/after, YAGNI/SSOT/SOLID rechecks, performance evidence where applicable,
runtime commands, native gates, and any blocker. Never claim completion from a
line delta alone.
