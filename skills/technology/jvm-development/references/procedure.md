# JVM development procedure

1. Read the Maven or Gradle owner, wrapper version, Java toolchain, Kotlin target,
   module graph, dependency constraints, and generated-source configuration.
2. Preserve public binary and source compatibility unless the approved change
   explicitly breaks it. Keep nullability and platform-type boundaries explicit.
3. Prefer immutable values and sealed or algebraic domain states where supported
   by the selected language level. Do not force records, data classes, streams,
   coroutines, or a framework where the project contract differs.
4. For Kotlin coroutines and Java concurrency, propagate cancellation and
   interruption, preserve structured ownership, and never detach unbounded work.
5. Translate exceptions only at an owning boundary and preserve the cause. Avoid
   broad catches and blocking calls on event-loop or coroutine dispatch threads.
6. Run the real application or library path first, followed by the repository's
   focused compile, static-analysis, test, packaging, and compatibility tasks.

Use the project's real integration test facilities. A specific mocking library,
container runtime, coverage percentage, or test layout is not universal law.
