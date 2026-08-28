# Operational hardcode extermination procedure

## Critical runtime prohibition

A hardcode is any operator-, deployment-, environment-, tenant-, or
installation-controlled value embedded outside its declared owner. Confirmed
hardcodes are critical, release-blocking defects. Typical consequences include
wrong-environment writes, state corruption, data loss or duplication, credential
exposure, security-boundary crossing, nonportable builds, and false-green tests.

Never accept, defer, suppress, document around, or retain the old value beside
the new contract. Moving a literal into another local constant, environment
variable, wrapper, template, or fallback does not fix ownership.

## Establish the owner

Read the repository's configuration schema, typed settings facade, manifests,
generators, CLI contract, and runtime construction path. For each operational
value identify:

- the single canonical owner and its type, validation, and required/optional
  semantics;
- every producer, consumer, projection, example, fixture, and test;
- the environments or deployments that must provide it;
- the exact failure required when it is absent, malformed, or inconsistent.

If no owner exists, design one at the lowest shared boundary before rewiring
consumers. Do not invent a second configuration system or read environment
variables directly when the project has an owner facade.

## Semantic inventory

Trace behavior rather than deleting literals by regex. Inspect:

- URLs, hosts, ports, database names, model/provider identifiers, branch names,
  filesystem paths, tenant IDs, credentials, feature decisions, timeouts,
  thresholds, and deployment modes;
- duplicated defaults across code, Make, shell, CI, containers, tests, docs,
  templates, and generated projections;
- `getenv` defaults, optional constructor values, CLI defaults, and lookup chains
  that silently select an operational value;
- tests that pass only because production values are embedded, and generators
  that copy literals instead of consuming the owner model.

For each confirmed path record the value class, current owner violation,
affected runtime, canonical destination, consumers to rewire, and injected
missing/invalid-value test. Never persist this inventory as a substitute tracker.

## Distinguish legitimate invariants

A literal is valid only when semantic evidence proves it is fixed by mathematics,
a cited protocol or file format, or an immutable domain rule; it has a meaningful
name where reuse or clarity requires one; and tests protect the invariant. Test
fixtures may use isolated example values that cannot reach production and do not
claim to be configuration defaults.

An endpoint, port, model, credential name, branch, path, timeout, or environment
choice is never made legitimate merely by naming it as a constant.

## Replace at the canonical owner

1. Write a failing test that injects a different, missing, or malformed value at
   the real construction boundary.
2. Add or extend the existing typed schema and validation primitive.
3. Make required operational fields truly required. Do not add implicit defaults,
   aliases, multi-source lookup, legacy readers, or old/new coexistence.
4. Inject the validated owner object into every consumer; do not let consumers
   scrape files or ambient environment state.
5. Regenerate projections through the owner and prove a second run is empty.
6. Delete the literal, duplicate defaults, compatibility paths, obsolete tests,
   fixtures, examples, and documentation.
7. When configuration fails, preserve the cause. The owning CLI writes an
   actionable error to `stderr` and exits nonzero. If correction is outside the
   authorized scope, the agent exposes the exact unresolved warning or blocker
   in its final response.

## Failure matrix and closure

Test at least missing, empty, malformed, wrong-environment, conflicting-source,
and projection-drift cases. Prove that no consumer runs, no alternate source is
selected, no partial artifact is published, and the causal error reaches the
caller.

Repeat semantic searches for the old values and alternate lookup paths. Run
runtime, unit, integration, static, security, generation fixed-point, and
projection gates. A warning, fallback, cached success, or successful exit after
configuration failure is a blocking defect, never completion evidence.
