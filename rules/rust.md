---
globs: ["*.rs", "**/*.rs", "Cargo.toml"]
description: Rust facts its compiler and linters do not enforce
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Rust

The project's declared toolchain and Cargo workspace own builds, features and
dependencies; no other repository's architecture is imposed. Failure travels as `Result`
through `?` and is never discarded; `unwrap` and `expect` appear only in tests or behind
an invariant the project documents. Lifetimes are written only where the compiler needs
them or they clarify a public contract. Public APIs document their contract, and every
`unsafe` block states its local invariant and passes the repository's safety review.
Everything else is the [law](law.md).
