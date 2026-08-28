# Dart and Flutter development procedure

1. Before effects, read project law, package manifest, SDK constraints, analysis
   options, dependency graph, platform targets, generated owners, state/routing
   architecture, public consumers, runtime, and native gates.
2. Preserve null-safety and public API contracts. Prefer `final` and immutable
   state where mutation is not required; use exhaustive pattern matching for
   closed states when supported by the declared SDK.
3. Await owned futures. Do not detach work, retry, select alternate state/routing
   paths, or catch failure into a warning or neutral UI value. Preserve the first
   error and lifecycle ownership.
4. In Flutter code, keep build functions free of side effects, dispose owned
   controllers and subscriptions, and verify liveness before using UI context
   after an asynchronous gap.
5. Change annotated sources rather than generated Dart files. Keep routing,
   state management, serialization, and dependency injection consistent with
   the existing project architecture.
6. Run the affected Dart or Flutter runtime path, then the project formatter,
   analyzer, unit/widget/integration tests, build, and configured golden checks.

Do not impose a state library, mocking library, folder layout, golden-update
command, or coverage target that the project has not selected. Missing evidence
stops with zero effects; build/test failure remains causal, cleanup attaches any
secondary failure, and obsolete/generated paths leave no residue.
