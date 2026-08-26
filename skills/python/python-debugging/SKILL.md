---
name: python-debugging
description: "Debug functional issues in Python using specs, logs, and observed behavior. USE FOR: feature not working as specified; runtime errors; scoping a problem before fixing. DO NOT USE FOR: writing new code patterns (python-production); parallelizing (python-parallelization); config schema evolution (config-schema-migrator)."
license: MIT
metadata:
  bundle: python
  scope: universal
---

# Python Debugging

Hypothesis-driven investigation. Fix only after root cause is proven with evidence.

## Loop

1. **Intake** — spec, exact errors/logs, repro steps, env, recent changes.
2. **Scope** — what works / fails / unknown; regression or new? smallest repro case as a failing test.
3. **Hypotheses** — ≥2 candidates with evidence for/against and a test each.
4. **Investigate** — trace data flow INPUT → PROCESSING → OUTPUT → SIDE EFFECTS; temporary debug logging at boundaries (`logger.debug("... %r", value)`), removed before commit.
5. **Root cause** — confirmed cause + file:line evidence + causal chain + eliminated hypotheses.
6. **Fix** — minimal change at the root cause; regression test written first; then full gates.

## Fast checks

- `NoneType` errors → who returned None unexpectedly? Check that call first.
- Mutable default args accumulating state → `def f(items=None)`.
- Missing `await` → coroutine object instead of result.
- Circular import → defer import into the function.

## Critical rules

- Never fix symptoms; no workaround without root-cause note.
- Debug artifacts never survive the cycle.
- Templates: [references/investigation-templates.md](references/investigation-templates.md).
