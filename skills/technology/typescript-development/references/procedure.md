# TypeScript development procedure

1. Read `tsconfig` inheritance, package exports, runtime targets, module format,
   package-manager lock, build graph, and test configuration.
2. Parse external input at the boundary into explicit domain types. Use `unknown`
   until validation proves a value; do not introduce `any`, unsafe assertions,
   or ignored diagnostics to obtain green.
3. Preserve ESM/CommonJS, browser/server, and synchronous/asynchronous boundaries.
   Do not change public exports or emitted formats incidentally.
4. Make promise ownership explicit. Propagate cancellation where the runtime
   supports it, handle rejected work, bound concurrency, and release timers,
   streams, sockets, and listeners.
5. Prefer discriminated unions for closed states and exhaustive checks for
   control-flow completeness. Keep runtime validation distinct from static types.
6. Exercise the real package or application path, then run the project's focused
   formatting, lint, type, test, and build commands.

Do not assume React, a bundler, a test runner, a package manager, or one module
format merely because TypeScript is present.
