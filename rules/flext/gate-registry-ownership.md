---
description: Enforcement gates derive their vocabulary from a single registry SSOT; frozen enumerations and duplicate config readers are defects
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# Gate registry ownership (derive, never enumerate)

Born from the flext-gov program (WS-F2/F4, 2026-09-11): a budget gate shipped
with a frozen 15-entry `required_gates` set in the gate class, an
`except ImportError: return set()` in a consumer-grammar detector, a
`_FLEXT_PREFIXES` copy of a constant the core family surface already derives,
and two gates each reading `[tool.flext.project]` their own way. Every one of
those localized a fact the SSOT already owns.

- A gate's target set, severity vocabulary, and SARIF row must derive from
  ONE owner (`c.Infra.SARIF_TOOL_INFO` / `ALLOWED_GATES` in flext-infra).
  Any second enumeration of the same fact in a gate class is a defect; fix
  the gate, not the rule.
- Family membership, legal symbols, and fix hints derive at runtime
  (`__all__`, `_LAZY_IMPORTS`, `importlib.metadata`, family-surface
  derivation) — never from a hardcoded prefix, roster, or bypass list.
- "Config unreadable" must fail loud with its cause. A swallowed exception
  that collapses a broken file into "absent config" silently changes gate
  semantics for every consumer.
- When two gates need the same config read, one owner helps; a per-gate
  reimplementation fails duplication gates and drifts on the first change.
- Success payloads are typed values (e.g. `r[int]` byte counts);
  `FlextResult[None]` and success-with-`None` are contract violations.

See also: `flext-venv-hermeticity.md`, `scanner-closure.md`.
