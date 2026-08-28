# Inline simplification procedure

## Purpose and boundary

Simplification is part of implementation, not a postponed cleanup phase. Apply it
to every code unit generated or changed before leaving that unit. A unit is the
smallest cohesive function, type, module section, query, configuration owner, or
test changed to deliver the current behavior.

The canonical sequence lives in `search-first`; do not reproduce it here. Consume
the necessary behavior, authority map, and optional design boundary already
selected upstream. Simplify each cohesive implementation unit immediately and the
post-DRY graph once. Never duplicate discovery, authority selection, boundary
design, or structural remediation inside `simplify`, and never turn the handoffs
into a recursive loop.

## Per-unit inline pass

First implement all behavior required from that unit by the active acceptance
criteria. A shorter partial implementation is a defect.

Then, before moving on:

- remove redundant branches, nesting, temporary state, conversions, wrappers,
  duplicated expressions, and comments that only narrate the code;
- prefer established project/library primitives and the canonical owner already
  identified by `search-first`;
- keep names descriptive, control flow explicit, functions cohesive, and error
  propagation causal and visible;
- retain public documentation and document non-obvious invariants at their owner;
- keep a local expression inline when extraction would create an abstraction with
  no second semantic consumer;
- preserve public interfaces, ordering, side effects, exception types and causes,
  security boundaries, observability, and measured performance characteristics;
- update focused tests for the complete behavior without weakening assertions or
  replacing runtime proof with mocks.

For existing behavior, establish the smallest canonical baseline before editing.
For new behavior, use the approved contract and failing/acceptance test as the
baseline; do not claim behavior preservation for behavior that did not exist.
Run the narrow runtime or behavioral check after the unit is complete and again
after any later structural change invalidates that evidence.

## Structural handoff to DRY

Do not turn a local edit into a repository sweep. Hand the affected graph to
`dry` only when callers and owners prove at least one structural condition:

- the same rule or knowledge is implemented by multiple owners;
- a class or module owns unrelated policy, persistence, transport, formatting,
  and orchestration responsibilities;
- obsolete paths must be removed and consumers rewired atomically;
- repeated I/O or computation spans units and requires measured remediation;
- a local simplification would merely move complexity into another file.

`ssot` owns authority selection. `dry` owns cross-file rewiring, god-pattern
decomposition, obsolete-code extermination, and scoped Tokei or performance
evidence. `simplify` owns only the readable final shape of the changed units.

## Prohibited shortcuts

- code golf, dense boolean puzzles, hidden control flow, metaprogramming for line
  reduction, arbitrary line limits, or Tokei as a quality score;
- premature helpers, generic frameworks, utility bags, or indirection without a
  current semantic consumer;
- deleting validation, error handling, observability, types, tests, or contract
  documentation to make code shorter;
- fallback, suppression, hardcoded results, compatibility residue, or old and new
  owners coexisting;
- editing generated output instead of its generator;
- repeatedly alternating between `simplify` and `dry` after their defined pass;
- claiming completion without real runtime and the affected native gates.

## Evidence

Report the complete behavior delivered, YAGNI/SSOT/SOLID decisions, units
simplified, any structural handoff to `dry`, all rechecks, and exact runtime plus
native-gate evidence. If a blocker prevents proof, report the command or missing
authority and leave the result explicitly unfinished.
