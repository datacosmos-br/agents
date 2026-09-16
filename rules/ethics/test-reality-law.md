---
description: Test reality law — non-adherent tests are removed; runtime is the authority
capsule_summary: |
  Universal law (operator ruling 2026-09-16): tests that do not adhere to the
  quality standards are REMOVED. Tests must test reality — what the modules do —
  through public interfaces. Everything else can be discarded. What counts is
  the runtime, not the tests.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Test reality law (universal)

1. Tests validate reality — observed runtime behavior of modules through their
   PUBLIC interfaces (facades, typed surfaces).
2. Tests that do not adhere to the quality standards (mocks, fakes, private
   construction, hardcoded project-owned values, assertions on internals) are
   REMOVED, not accommodated.
3. When a test contradicts observed canonical runtime behavior, runtime wins:
   the test is corrected or removed, never the runtime bent to the test.
