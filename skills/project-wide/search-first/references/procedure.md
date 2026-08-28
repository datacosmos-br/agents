# Search-first procedure

## Gate

No implementation, dependency addition, abstraction, or detailed solution design
may precede project discovery. The depth is proportional to the change, but even a
small known-file edit must confirm the governing instructions, target owner, and
affected consumer or test.

Search-first does not mean web-search-first. Local runtime and repository evidence
establish how this project works. Canonical library documentation is used only
after the installed dependency and version are known, or when a missing capability
must be evaluated.

## Establish the project contract

1. Resolve the repository root and read applicable instruction files.
2. Inspect the architecture guide, ADR index, module/package layout, build facade,
   manifests, lockfiles, generated-file markers, and configured native gates.
3. Identify the public runtime entry point and the canonical owner of the behavior.
4. Record conflicts or missing authority explicitly. Never choose a convention by
   guesswork or copy one from an unrelated repository.

Use the active project's structural search surface. If a maintained code index is
already available, query its architecture, symbols, callers, and dependencies.
Otherwise use repository-native tools and targeted `rg` searches. Do not initialize
or replace project tooling merely to satisfy this skill.

## Build one evidence packet

Capture the smallest sufficient packet before editing:

- applicable project instructions and architectural authority;
- public entry point, canonical owner, callers, registrations, and generator;
- matching or adjacent implementations and their semantic differences;
- manifests, lockfiles, installed versions, and approved dependency adapters;
- current consumer, acceptance criterion, public runtime, and native gates.

The packet is working evidence, not a new document or tracker. Keep it in the
active response or authorized delivery record. Reuse it throughout the change.
Refresh only an invalidated field when an edit changes its owner, consumer graph,
dependency set, generated ownership, or runtime contract. Do not restart the
whole search merely because the next implementation step begins.

## Search for existing capability

Search by both names and behavior:

- definitions, imports, callers, interfaces, facades, adapters, and registrations;
- tests, fixtures, examples, migrations, configuration keys, generators, and
  generated projections;
- similar implementations whose semantics differ in important ways;
- dependency manifests, lockfiles, installed versions, and existing API usage;
- current consumers that justify the requested behavior.

Read the decisive source and its callers rather than relying on filenames or a
search snippet. Search deleted or historical code only when current evidence points
to a regression or superseded contract; history is not an active owner.

For third-party behavior, inspect the pinned version and primary documentation.
Do not add a package until the inventory proves the project and its current
dependencies lack the needed capability. Do not recreate a library primitive
locally when its supported API already satisfies the contract.

## Make the implementation decision

Choose in this order, based on semantic fit rather than line count:

1. Reuse an existing project capability unchanged.
2. Extend the canonical owner and rewire every affected current consumer.
3. Use an existing approved dependency through the project's established adapter.
4. Implement the smallest missing behavior required by a real current consumer.

Pass the packet through the canonical `yagni` skill before selecting new code; it
owns necessity decisions and removes scope without a current requirement,
consumer, and reachable runtime. Pass every surviving fact, policy, schema,
contract, and configuration surface through `ssot`; it owns selection of the one
writable authority and the roles of generators and projections. Apply `solid` only
to necessary module, type, service, API, or dependency boundaries. `dry` removes
proven structural duplication using the SSOT decision; it does not choose another
authority or merge superficially similar behavior.

If new code remains necessary, state the evidence that ruled out reuse and name
the real consumer. Follow the established architecture and public facade; do not
create a parallel owner, helper collection, or one-off dependency path.

## Execute the bounded cycle

1. Run the `yagni` necessity gate, the `ssot` authority gate, then the `solid`
   boundary check when relevant.
2. Implement the selected smallest necessary change at the canonical owner.
3. Apply `simplify` inline after each cohesive edit: remove accidental nesting,
   branches, indirection, and local repetition without changing behavior or
   expanding scope.
4. Continue directly to runtime proof when the affected graph has one clear owner
   and no confirmed structural debt.
5. Invoke `dry` only when the packet proves semantic duplication across owners,
   an oversized multi-responsibility unit, or repeated runtime work, and that
   remediation belongs to the authorized current outcome. Pass the packet to
   `dry`; that invocation must not call `search-first` again unless its evidence
   has actually become invalid.
6. After `dry` rewires consumers and removes superseded paths, recheck `yagni`,
   `ssot`, and `solid`, then apply one final `simplify` pass to the changed graph.
7. Run the real public runtime, then the affected native gates. A changed owner,
   dependency, or contract requires refreshing the relevant packet field before
   continuing.

This is a bounded pipeline, not a recursive loop:

`search-first -> yagni -> ssot -> optional solid -> implement + simplify inline -> optional dry -> yagni/ssot/solid recheck -> simplify final -> runtime -> gates`

Do not invoke `dry` for ordinary local cleanup, anticipated future duplication,
raw line count, or the mere existence of a long cohesive file. Do not invoke
`simplify` as a substitute for missing architecture evidence or structural
rewiring.

## Fail closed

Block implementation when the repository cannot be resolved, applicable project
rules are unavailable, generated ownership is unknown, architecture authorities
contradict one another, the relevant dependency version cannot be established, or
the requested consumer is hypothetical. Report the exact missing evidence and one
targeted action needed to resolve it.

Never turn incomplete search into a fallback design. Never claim that no code
exists based on a single term, directory, or tool. Never hide an inconclusive
search behind a confident implementation plan.

## Handoff evidence

After implementation, report the packet, YAGNI decision, SSOT authority and
projection decision, SOLID boundary decision, code reused or extended, current
behavior added, inline simplification, whether structural DRY was proven and
invoked, all rechecks, final simplification, and decisive runtime plus gate
outputs. Never report speculative reuse, unmeasured efficiency, or a completed
cycle when any required stage is still red.
