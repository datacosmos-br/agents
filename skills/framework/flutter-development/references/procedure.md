# Dart and Flutter development procedure

1. Read the package manifest, SDK constraints, analysis options, dependency
   graph, platform targets, and generator configuration.
2. Preserve null-safety and public API contracts. Prefer `final` and immutable
   state where mutation is not required; use exhaustive pattern matching for
   closed states when supported by the declared SDK.
3. Await owned futures or mark intentional detached work through the project's
   approved primitive. Preserve cancellation, error context, and lifecycle
   ownership.
4. In Flutter code, keep build functions free of side effects, dispose owned
   controllers and subscriptions, and verify liveness before using UI context
   after an asynchronous gap.
5. Change annotated sources rather than generated Dart files. Keep routing,
   state management, serialization, and dependency injection consistent with
   the existing project architecture.
6. Run the affected Dart or Flutter runtime path, then the project formatter,
   analyzer, unit/widget/integration tests, build, and configured golden checks.

Do not impose a state library, mocking library, folder layout, golden-update
command, or coverage target that the project has not selected.
