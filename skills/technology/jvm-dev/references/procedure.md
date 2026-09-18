# JVM development procedure

1. Before effects, read project law, the Maven or Gradle owner, wrapper version, Java
   toolchain, Kotlin target, module graph, dependency constraints, generated-source
   owner, public consumers, runtime, and native gates.
2. Preserve public binary and source compatibility unless the approved change explicitly
   breaks it. Keep nullability and platform-type boundaries explicit.
3. Prefer immutable values and sealed or algebraic domain states where supported by the
   selected language level. Do not force records, data classes, streams, coroutines, or
   a framework where the project contract differs.
4. For Kotlin coroutines and Java concurrency, propagate cancellation and interruption,
   preserve structured ownership, and never detach unbounded work.
5. Let the first exception and causal chain escape unchanged. Catch only for
   cleanup/rollback, attach any secondary failure, and rethrow the original. Avoid
   blocking event-loop or coroutine dispatch threads.
6. Run the real application or library path first, followed by the repository's focused
   compile, static-analysis, test, packaging, and compatibility tasks.

Use the project's real integration test facilities. A specific mocking library,
container runtime, coverage percentage, or test layout is not universal law. Missing
owner evidence stops with zero effects; wrapper, compiler, test, timeout, signal, or
packaging failure is never retried or replaced by another build path.
