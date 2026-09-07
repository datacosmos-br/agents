---
name: go-development
description: 'go, module development, toolchain detection'
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:marker:go.mod","detect:marker:go.work","effective:2026-08-28","route:project","subject:go","usage:router"]'
  version: 1.0.0
---

# Go Development

Activate from a detected Go module/workspace. Before edits, resolve project law,
Go version, modules, generated owners, public APIs and consumers, runtime, and
native format/vet/static/race/test/build commands.

Keep packages cohesive and dependencies acyclic. Preserve raw errors or the
project's typed causal chain; never discard, aggregate, retry, log-and-continue,
or replace failure with `nil`. Pass `context.Context` explicitly across
cancellable I/O and never store it in a long-lived struct.

Prefer synchronous code. Add goroutines only with a current requirement, explicit
owner, cancellation, bounded lifetime, race-safe state, first-error propagation,
and cleanup that re-raises the original cause. Rewire consumers atomically and
remove detached/old paths.

Run the public behavior and project-native gates. A child nonzero, timeout,
signal, race, or incomplete effect remains causal; no alternate toolchain or
partial result makes it green.
