---
description: Apply the mandatory engineering decision and delivery sequence.
capsule_summary: |
  Every implementation: research the owner first, cut scope without a current
  consumer, elect one writable authority, make every other copy a generated
  projection, improve the owner in place, never a parallel one beside it,
  implement through the owner, remove duplication, keep
  discoverable enumerations as authority data validated by grammar, never
  fixed lists or absolute paths, then exercise runtime and run every gate
  before changing phase.

  At a cross-boundary failure, prove the producer's contract and fix the wrong
  side; never bend a correct owner for an invalid consumer.

  Hardcodes, normalized failure, failover, retry, fallback, partial execution
  and unevidenced success are defects. The first exception escapes with its
  traceback and cause.

  A managed repository keeps its exact declared-identity remote. A broken alias
  never authorizes the generic form, and an agent never writes the operator's SSH
  configuration or keys — identity is corrected in git, or reported.
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-10-01","route:both"]'
---

# Engineering core

For every implementation:

1. Research repository owners, dependencies, and canonical documentation.
2. Remove scope without a current requirement or consumer (YAGNI).
3. Elect one writable authority; every other copy is a generated projection (SSOT).
   Improve the owner in place: writing a parallel replacement, renderer, or registry
   beside the owner is a violation — consume the owner's projection, never copy its
   contract. Enumerations discoverable through the owning authority are data, never
   code: the authority owns instances, contracts validate structure and grammar, and a
   fixed list in code that duplicates what the SSOT already derives is a bypass to
   exterminate. Absolute paths and references outside the repository are hardcodes.
4. Apply SOLID only to a responsibility or dependency boundary under change.
5. Implement through the owner and simplify without weakening behavior.
6. Remove duplication and god components; recheck YAGNI, SSOT, SOLID.
7. Exercise runtime behavior, run every applicable native gate, and complete the
   approved landing cycle before changing phase.

At a cross-boundary failure, prove the producer contract and output. Fix its owner when
invalid or the receiver when it conforms. Never alter a correct adjacent owner for an
invalid consumer; symptom workarounds are defects.

Hardcodes, normalized failure, failover, retry, fallback, compatibility, partial
execution, application keyring reads, and unevidenced success are defects. Typed owners
keep defaults. The first exception escapes its CLI with traceback and cause.

Every one of these defects is a workaround to exterminate at its owner, never to
accommodate (tracker memory `operator-ruling-2026-10-01-total-extermination`). The
same holds for the classes below; the hardcode class is stated precisely first, and
each of them is replaced by rules, configuration, and SSOT functions (tracker memory
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

Exterminating them shrinks the code; growth to accommodate one is itself a defect.

Every cleanup follows one order, declared only here (tracker memory
`operator-ruling-2026-10-01-total-extermination`); every other rule, skill, command,
and agent profile references it:

1. Exterminate absolutely every violation in scope first, with no heavy validation
   between extermination steps.
2. Then rewire every consumer to the final owner.
3. Then rewrite the tests to the real runtime behavior and run them. Validation runs
   once, at the end.

The order is the work sequence inside one cutover, not a landing sequence: the cutover
still lands atomically, with zero residue and every consumer rewired, and a scoped WIP
commit between steps is persistence, not validation.

Git, runtime, build, and tests are baseline. Every other executable is an authorized,
selected capability; installation or PATH presence never selects it. Do not load,
locate, probe, or gate dormant capabilities. A selected invalid capability fails without
fallback and requires only non-derivable values.

A portable library owns only primitives that remain valid without a particular host
application. Host-wide indexes, daemons, forges, language servers, and refactor
orchestration belong to the runtime control plane that operates them. A lower library
may consume an available host capability only through its public command, hook, or MCP
contract; importing the host application as a library, reproducing its state, or
creating a substitute runtime is forbidden. An absent and unselected host capability is
not an error. Once explicitly selected and available, its first failure propagates
without fallback.

Remote access follows the repository's current Git and forge configuration. Never
rewrite protocols, create identity aliases, or mutate user SSH configuration as a
prerequisite for ordinary Git operations.

A broken account alias never authorizes the generic form. When the declared identity
stops resolving, the remote stays declared and the alias is restored by its owner;
migrating repositories to a generic remote to regain access converts one outage into a
standing violation. The operator's SSH client configuration and keys are never written
by an agent — not to repair identity, not to deploy a fragment, not to restore access.
Identity is corrected in git; anything that requires editing SSH configuration is
reported to the operator instead.

A check whose declared capability is unavailable — an external token, or a host
capability such as Docker or a remote service that the environment (CI included) lacks —
is not executed and is recorded as typed `NOT EXECUTED` with its reason: never green,
never counted as passed, never a runtime skip. A missing token does not block offline
gates, landing, or post-merge proof. A missing host capability does not turn the run
that lacks it red, and the behavior it covers counts as proven only by a run where the
capability is present. Direct invocation selects the check: the capability becomes
required and any failure escapes without skip, catch, fallback, or normalization.

Compose with `generalized ownership` (rule file), `strict execution` (rule file),
`runtime evidence` (rule file), `storage isolation` (rule file), `security closure`
(rule file).
