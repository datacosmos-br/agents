---
globs: ["*.ts", "*.tsx", "**/*.ts", "**/*.tsx", "tsconfig.json"]
description: TypeScript facts its compiler and linters do not enforce
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# TypeScript

The project's declared runtime, TypeScript version, module system, package manager and
framework apply; no other repository's architecture is imposed. The compiler runs the
strictest checks the project supports, with no `any`, unchecked casts or blanket
suppressions. Nullability is explicit, and untrusted data is validated once at the
boundary by the project's declared schema owner. Bindings and data are immutable where
practical, and asynchronous flow uses `async`/`await`. Everything else is the
[law](law.md).
