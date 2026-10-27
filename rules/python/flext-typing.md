---
globs: "**/*.py"
description: FLEXT typing is strict; Any and object are grave violations
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-26","route:both"]'
---

# FLEXT typing: strict always — `Any` and `object` are grave violations

This rule applies only when the active project profile is `internal_flext`. A
third-party fork is excluded even when it contains Python files or depends on
FLEXT-compatible packages.

Using `Any` or bare `object` in a Python annotation is a grave violation, in any module,
test, executable documentation or scratch script that lands in a governed tree.
Typing is strict everywhere, without temporary weakening.

Reuse contracts from their declaring owner at the strongest supported precision.
Data fields retain their originating model contracts; behavioral dependencies use
the owning typed ports. Consume project aliases and protocols through their declared
facades. Do not replace a Pydantic data model with a behavioral protocol or copy an
owned callable into a weaker consumer-local declaration to obtain a passing checker.

- Use `TYPE_CHECKING` only when the annotation is not required for runtime validation.
  Runtime model annotations resolve through runtime-safe imports at their declaring
  owner; static success cannot replace model completeness at import.
- The branch-matched project law and accepted topic ADR own facade composition,
  alias shape and the exact runtime floor. Use its native syntax and Pydantic
  generation; do not restore compatibility imports or Pydantic v1.
- No `# type: ignore` / `noqa` shims — fix the type at its root.
- Search the existing contract first. When extension, improvement or generalization
  is necessary, change that owner and propagate it to consumers; never create a
  parallel alias, model or protocol to hide the mismatch.
