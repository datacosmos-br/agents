---
description: Apply the mandatory engineering decision and delivery sequence.
capsule_summary: |
  Every problem in every session and project requires researched contracts,
  reproduction, debugging and tracing that prove the causal owner before repair.
  Hypotheses guide investigation only; never edit speculatively or try random
  solutions. Follow canonical rules without invented behavior or exceptions.
  Validate every adjustment immediately at the original failing boundary; failure
  returns to diagnosis before another edit.

  Map through CRG and research owners first. Require a current consumer, one writable
  authority and generated projections; improve the owner, never a parallel replacement.
  Remove duplication; discoverable enumerations remain authority data validated by
  grammar, never fixed lists or absolute paths. Align docs before code, runtime before
  tests, applicable gates and landing before phase advancement.

  At a cross-boundary failure, prove the producer's contract and fix the wrong
  side; never bend a correct owner for an invalid consumer.

  Hardcodes, hidden failure, retry, fallback and false success are defects.
  Typed branches and causal exceptions follow the fail-loud boundary owner.

  Keep the declared Git identity. A broken alias never permits a generic remote
  or operator SSH/key edits; correct identity in Git or report it.
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-10-29","route:both"]'
---

# Engineering core

These standards govern all first-party phases. External forks follow the verified
upstream-forks contract. Reconcile project requirements with the canonical
cross-project and cross-agent governance owner, never a divergent local copy.
FLEXT also obeys its stricter local contracts.

The 2026-10-26 operator ruling recorded in `ag-h1k1` governs every session and task:
use selected,
functioning CRG CLI, MCP and specialists under `crg` and `dispatch-agent`, applicable
skills and ADRs. Selection authorizes no installation, removal, destruction or unrelated
commands. Repair causal owners under [tool ownership](../workflow/declared-tool-ownership.md).
Before advancing, converge Make/CLI, gates, docs, ADRs, skills and Beads with measured
behavior and integration. Adopt and fix forward; unresolved warnings remain pending.

## Evidence before every repair

The 2026-10-26 correction follows
[causal diagnosis](../workflow/runtime-is-reality.md#causal-diagnosis) for every
problem, session and project; investigation precedes repair, not patch-and-see.

For every implementation:

1. Map through CRG and confirm source (`operator-ruling-20261022-crg-every-session`);
   `crg` owns freshness, lane seeds, watches and verbs. Research owners, dependencies,
   README, AGENTS, guides, ADRs, approved plans, specifications, selected tracker,
   skills, rules and command contracts. Update affected owners before code;
   consultation alone never admits stale instructions. Verify propagated identities;
   regenerate through declared owners, never edit installed output.
2. Remove scope without a current requirement or consumer (YAGNI).
3. Elect one writable authority; every other copy is a generated projection (SSOT).
   Improve it in place; parallel replacements, renderers, registries and copied
   contracts violate ownership. Discoverable enumerations are authority-owned data;
   contracts validate grammar/structure, never duplicate instances as fixed lists.
   Absolute paths and outside-repository references are hardcodes.
4. Apply DDD, Clean Architecture and explicit DI at the responsibility and dependency
   boundaries under change; domain behavior does not depend on infrastructure details.
5. Implement through the owner without losing functionality or changing business rules
   unless the approved project plan or the operator explicitly authorizes that change.
   Specification changes require prior discussion and approval under
   [operator precedence](../coordination/operator-precedence.md).
6. Every execution branch follows DRY, YAGNI, SSOT, KISS and SOLID. Remove duplication,
   god components and over-engineering rather than adding parallel accommodation.
7. Exercise runtime behavior, run every applicable native gate, and complete the
   approved landing cycle before changing phase.

Across boundaries, prove producer contract/output; fix the nonconforming producer or
invalid receiver, never a correct adjacent owner or symptom workaround.

Transactions follow [atomic effects](../runtime/atomic-effects.md), including its
reader barrier and 2026-10-29 preservation/fix-forward supersession. Incremental gates
follow
[canonical commands](../workflow/canonical-commands.md); optimization preserves
the specification and required proof.

Hardcodes, hidden failure, failover, retry, fallback, compatibility, partial
success presented as complete, application keyring reads, and unevidenced success are
defects. Old signatures
follow only `zero residue`'s "Deprecated-signature window". Typed owners keep defaults.
Expected branches, optional defaults, causal translation, independent outcomes and
unexpected-error containment follow [fail loud](../runtime/fail-loud.md), amended by
[ADR-0021](https://github.com/datacosmos-br/agents/blob/dev/docs/adr/ADR-0021-operator-universal-rulings-runtime-truth.md#failure-boundary-supersession--2026-10-29).
The [Python consumer rule](../python/no-hidden-errors.md) applies that contract without
a second exception policy; it does not require every failure to escape globally.

Exterminate these defects at their owners, never accommodate them (tracker memory
`operator-ruling-2026-10-01-total-extermination`). Replace the following classes
with rules, configuration and SSOT functions (tracker memory
`operator-rulings-2026-10-01-governance`, rulings 7 and 11):

- a hardcoded value — path, URL, number, name, version, or limit — instead of its
  declared owner in configuration, settings, or constants; a tunable value is declared
  once in gated configuration with a per-project override, and guidance references its
  key, never the number;
- a dependency-injection violation — a service building its own infrastructure, reading
  global settings, probing capabilities, or depending on a concrete type where a
  protocol port belongs;
- coupling — an import against the layer direction, use of another package's private
  module, a cycle hidden by a local import, a library that knows its consumers, or
  behavior placed in a declaration layer;
- a hardcoded rule — validation or enforcement written as code instead of rule data
  applied by the generic engine;
- a hand-maintained registry, roster, allowlist, or mapping that duplicates what an SSOT
  function derives.

Accommodation growth is itself a defect.

Cleanup order (tracker memory `operator-ruling-2026-10-01-total-extermination`);
other artifacts reference this owner:

1. Exterminate every violation in scope at its proven cause. Validate each correction
   immediately through [causal diagnosis](../workflow/runtime-is-reality.md#causal-diagnosis)
   before dependent work.
2. Then rewire every consumer to the final owner; while consumers remain, the old
   signature lives only as the marked pass-through of the `zero residue` rule's "Deprecated-signature window" section,
   deleted when its census reaches zero.
3. Rewrite tests to the proven runtime behavior and run them. Run the complete gates
   after the cutover; they never replace immediate verification of each correction.

The order is the work sequence inside one cutover, not a landing sequence: the cutover
still lands atomically, with zero residue and every consumer rewired, and a scoped WIP
commit between steps is persistence, not validation.

For the bounded `flext-0029c` native-bootstrap route declared in
`rules/workflow/canonical-commands.md`, the cleanup order above does not
prohibit repeated real native runtime QA, causal repair revalidation or convergence
proof. Align documentation first, repair and rewire the current owner, prove the
installed subsystem and cold bootstrap, then change tests last. This exception
does not authorize unchanged retries, fake evidence or premature suite-driven design.

Git, runtime, build, and tests are baseline. Every other executable is an authorized,
selected capability; installation or PATH presence never selects it. Do not load,
locate, probe, or gate dormant capabilities. A selected invalid capability fails without
fallback and requires only non-derivable values.

A portable library owns host-independent primitives. The runtime control plane owns
host indexes, daemons, forges, language servers and refactor orchestration. Libraries
consume available host capabilities only through public commands, hooks or MCP;
never import the host as a library, reproduce its state or create a substitute runtime.
An absent unselected capability is not an error; a selected capability's first failure
remains causal and visible through its responsible boundary, without fallback.

Remote access follows current Git/forge configuration. Never rewrite protocols,
create identity aliases or change user SSH configuration for Git operations. A broken
alias never authorizes a generic remote: preserve the declared identity and repair
through its owner. Agents never write operator SSH configuration or keys, including
repair, fragment deployment or access restoration. Correct identity in Git; report
required SSH configuration changes to the operator.

A check whose declared capability is unavailable — an external token, or a host
capability such as Docker or a remote service that the environment (CI included) lacks —
is not executed and is recorded as typed `NOT EXECUTED` with its reason: never green,
never counted as passed, never a runtime skip. A missing token does not block offline
gates, landing, or post-merge proof. A missing host capability does not turn the run
that lacks it red, and the behavior it covers counts as proven only by a run where the
capability is present. Direct invocation selects the check: the capability becomes
required and any failure remains red under the responsible failure-boundary contract,
without skip, fallback or success normalization.

Compose with `generalized ownership` (rule file), `strict execution` (rule file),
`runtime evidence` (rule file), `storage isolation` (rule file), `security closure`
(rule file).
