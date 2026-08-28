---
globs: ["*.ts", "*.tsx", "**/*.ts", "**/*.tsx", "tsconfig.json"]
---

# TypeScript rules

Use the project's declared runtime, TypeScript version, module system, package
manager, framework, and canonical command facade. Never impose a repository-
specific architecture on a generic TypeScript project.

- Enable the project's strictest supported type checks; do not use `any`,
  unchecked casts, blanket diagnostic suppression, or empty `catch` blocks.
- Model nullability and external input explicitly. Validate untrusted data once
  at the boundary with the project's declared schema owner.
- Prefer immutable bindings/data where practical and `async`/`await` for
  readable asynchronous control flow.
- Preserve structured errors and causes. A missing value is not permission to
  invent a default success.
- Run the real public runtime first, then every declared lint, format, type,
  test, build, security, and package gate affected by the change.
- Use project-local dependencies and physical files only: no symlink, path
  dependency to another checkout, cross-repository reference, inherited secret,
  or project state under `/tmp`.
- Install TypeScript technology skills only when project-local markers prove
  TypeScript. FLEXT content remains absent unless independent FLEXT detection
  succeeds.
