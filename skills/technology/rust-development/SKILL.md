---
name: rust-development
description: 'Develop Rust projects when Cargo.toml proves the Rust toolchain.'
license: MIT
metadata:
  aihub.tags: '["activation:detected","detect:marker:Cargo.toml","provenance:agents-owned","route:project","technology:rust","updates:manual","usage:router"]'
  version: 1.0.0
---

# Rust Development

Follow the active workspace's edition, feature policy, crate boundaries, public
APIs, and documented commands.

## Workflow

1. Read the workspace and crate `Cargo.toml` files plus project instructions.
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
