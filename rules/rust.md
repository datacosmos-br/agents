---
globs: ["*.rs", "**/*.rs", "Cargo.toml"]
---

# Rust rules

Use the project's declared Rust toolchain, workspace structure, features, and
canonical command facade. Never impose a repository-specific architecture on a
generic Rust project.

- Handle recoverable failure with explicit `Result`/`Option` semantics and
  `?`; do not discard a `Result`, panic for ordinary input, or invent a
  default success.
- Avoid `unwrap`/`expect` outside tests or proven invariants documented by
  project policy.
- Keep ownership and lifetimes explicit where they clarify public contracts;
  do not add annotations the compiler does not require.
- Document public APIs and safety invariants. Every `unsafe` block requires a
  local invariant and the repository's dedicated safety review.
- Run the real public runtime first, then every declared format, lint, type/
  check, test, build, documentation, security, and package gate affected by the
  change.
- Use project-local dependencies and physical files only: no symlink, path
  dependency to another checkout, cross-repository reference, inherited secret,
  or project state under `/tmp`.
- Install Rust technology skills only when project-local markers prove Rust.
  FLEXT content remains absent unless independent FLEXT detection succeeds.
