# YAGNI necessity and extermination procedure

## Strict necessity law

Every proposed or retained behavior, configuration key, flag, mode, abstraction,
interface, dependency, adapter, hook, cache, migration path, and extension point
must map to all three:

1. an approved current acceptance criterion or invariant;
2. at least one real current consumer;
3. a reachable supported runtime or build path.

“Might need,” future scale, possible reuse, symmetry, completeness, framework
fashion, or hypothetical consumers do not satisfy the gate. A confirmed
future-only surface in the authorized affected graph is a blocking design defect;
remove it at the owner in the same change rather than hiding it behind a flag,
deprecation, fallback, shim, alias, or documentation promise.

## Flow contract

The canonical sequence lives in `search-first`; do not copy or restart it here.
Consume its evidence packet, output the smallest current concept set to `ssot`,
and accept one post-rewiring recheck. YAGNI decides whether a concept should exist;
it does not select its authority, design its boundaries, consolidate its
implementation, or choose its local code form.

## Build a necessity matrix

For each proposed addition and suspicious retained surface, identify:

- exact current requirement or invariant;
- concrete caller, user, job, service, test, build, or deployment consumer;
- public/runtime path that reaches it;
- authority candidates, writers, projections, and supported lifetime;
- decisive source evidence and negative-search coverage;
- keep, reduce, replace with existing capability, or delete decision.

Keep this matrix in the active response or authorized delivery evidence, never a
manual tracker or new repository ledger. Read decisive definitions,
registrations, construction roots, dynamic loaders, generators, generated
projections, manifests, and callers. Search by behavior as well as names. History
may explain intent but does not create a current consumer.

## Distinguish unused from required

Preserve behavior when evidence proves any current supported consumer, even when
usage is rare. Public compatibility, data migration, rollback safety, security,
compliance, recovery, observability, protocol conformance, and build portability
can be current requirements without frequent execution.

Tests alone are not product consumers when they protect only speculative code,
but contract tests can prove a supported public requirement. Telemetry absence is
insufficient when instrumentation is incomplete. Reflection, plugin discovery,
dependency injection, command registration, templates, generated code, and
external API consumers require semantic tracing before deletion.

Do not replace a future feature with generic infrastructure “for later.” Do not
externalize speculation into configuration, an interface, a dependency, or docs.
The smallest valid implementation handles the current acceptance cases and
explicit failure boundaries, nothing more.

## Atomic extermination

1. Protect every current supported behavior with public runtime or contract tests.
2. Resolve the unique authority through `ssot`, then remove the speculative
   behavior there.
3. Rewire current consumers to the smallest existing capability when applicable.
4. Use `solid` only for necessary responsibility and dependency boundaries.
5. Use `dry` when deletion crosses owners or exposes duplication, god patterns,
   dead adapters, or repeated work; delete all obsolete consumers, tests, flags,
   fixtures, examples, dependencies, configuration, and documentation atomically.
6. Apply `simplify` inline to every changed unit.
7. Search again for the removed identity and alternate construction paths. Old
   and new surfaces must not coexist.

## Verification

Run the real public runtime before general gates, after rewiring, and on the
integrated result. Exercise required positive behavior plus missing/unsupported
requests so removed future modes fail through the documented boundary rather than
silently rerouting. Run unit, integration, static, type, build, security,
generation, dependency, and projection fixed-point gates.

Report the current requirement and consumer for every retained addition, every
speculative surface deleted, dependencies/config/docs removed, SSOT authority and
projection decision, YAGNI/SSOT/SOLID rechecks, DRY structural work, simplify
result, runtime commands, and native gates. Never claim success merely because
code became smaller.
