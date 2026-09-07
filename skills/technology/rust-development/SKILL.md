---
name: rust-development
description: 'rust, cargo development, toolchain detection'
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:marker:Cargo.toml","effective:2026-08-28","route:project","subject:rust","usage:router"]'
  version: 1.0.0
---

# Rust Development

Follow the active workspace's edition, feature policy, crate boundaries, public
APIs, and documented commands.

## Workflow

1. Before effects, read project law, workspace/crate manifests, lockfile,
   toolchain, features, generated owners, public consumers, runtime, and gates.
2. Model invariants with types and ownership; prefer borrowing and explicit
   lifetimes only where they clarify real relationships.
3. Use `Result` and meaningful error context at fallible boundaries. Reserve
   panics for violated internal invariants, not expected runtime failures.
4. Keep unsafe code minimal, isolated, documented with its safety contract, and
   covered by focused tests.
5. Run the project's canonical formatting, Clippy, tests, feature checks, and
   build commands for the affected crates.

## Critical rules

- Do not silence lints or replace errors with `unwrap`/`expect` to obtain green.
- Do not broaden features or public APIs unintentionally.
- Treat generated files as outputs and edit their declared source instead.
- Preserve the first typed error, child nonzero, timeout, signal, or panic cause;
  never retry, fall back to another feature/toolchain, or publish partial output.
- Missing crate or safety evidence stops with zero effects.
