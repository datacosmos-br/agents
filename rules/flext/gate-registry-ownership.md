---
description:
  Enforcement gates derive their vocabulary from a single registry SSOT; frozen
  enumerations and duplicate config readers are defects
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# Gate registry ownership (derive, never enumerate)

Born from the flext-gov program (WS-F2/F4, 2026-09-11): a budget gate shipped with a
frozen 15-entry `required_gates` set in the gate class, an
`except ImportError: return set()` in a consumer-grammar detector, a `_FLEXT_PREFIXES`
copy of a constant the core family surface already derives, and two gates each reading
`[tool.flext.project]` their own way. Every one of those localized a fact the SSOT
already owns.

- A gate's target set, severity vocabulary, and SARIF row must derive from ONE owner
  (`c.Infra.SARIF_TOOL_INFO` / `ALLOWED_GATES` in flext-infra). Any second enumeration
  of the same fact in a gate class is a defect; fix the gate, not the rule.
- Family membership, legal symbols, and fix hints derive at runtime (`__all__`,
  `_LAZY_IMPORTS`, `importlib.metadata`, family-surface derivation) — never from a
  hardcoded prefix, roster, or bypass list.
- "Config unreadable" must fail loud with its cause. A swallowed exception that
  collapses a broken file into "absent config" silently changes gate semantics for every
  consumer.
- When two gates need the same config read, one owner helps; a per-gate reimplementation
  fails duplication gates and drifts on the first change.
- Success payloads are typed values (e.g. `r[int]` byte counts); `FlextResult[None]` and
  success-with-`None` are contract violations.

## Every custom validation is re-derived, not just gates (operator ruling, 2026-09-12)

<!-- Why: registers 2026-09-12 operator ruling R26; generalizes this owner's existing SSOT-derivation law past lint gates -->

The same law extends past linting gates to every custom validation, warning, or block a
project runs — hooks, guards, enforcement rules, MCP checks. Each one is re-evaluated
for the SSOT-derivation contract above: no hardcoded list/roster/prefix, a documented
rule it enforces, and no selective silencing or disabling once it is correctly
implemented. The validation's own logic consumes rules, data, config, and settings from
their typed SSOT in context; it never carries a literal list of its own. A failing
validation is fixed at its owner the moment it is found; genuine doubt about correctness
escalates to the operator rather than being silenced.

See also: `flext-venv-hermeticity.md`, `scanner-closure.md`.
