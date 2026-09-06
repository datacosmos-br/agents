---
name: runtime-language-level
description: 'runtime floor, precise typing, modern language capabilities'
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:selected-tag:internal","domain:language","effective:2026-09-04","policy:fail-loud","policy:no-fallback","policy:strict-execution","provenance:agents-owned","route:project","updates:manual","usage:router"]'
---

# Runtime language level

Activate only for an internal project. Resolve the minimum runtime from the
canonical manifest, then compare every compiler, formatter, linter, type checker,
editor, build, and CI target with it. Use precise contracts and native language
features available at that floor; remove compatibility syntax and branches for
older undeclared runtimes.

Do not hardcode a universal version. Route to the detected language skill for
language-specific syntax and gates. FLEXT resolves to Python 3.13 and Pydantic 2.
Conflicting or missing runtime ownership stops before code changes.

Never activate for `third_party_fork`; its upstream owns language level and
typing style.
