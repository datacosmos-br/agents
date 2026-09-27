---
description: Mimosa static advisory triage — trust boundaries, sink containment,
  disposition ledger
capsule_summary: |
  Operator ruling 2026-09-27 (mcb ADR 059): sealed scanners re-report disposed
  anchors forever, so dispositions live in beads and follow rules D1-D5 —
  environment overrides are operator trust boundaries; sinks enforce their own
  containment with a warning and a RED-proven test; vendored test fixtures sit
  outside the production dependency graph; client-side sentinels are not
  credentials; a re-reported anchor with a bead disposition closes by reference.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-27", "route:both"]'
---

# Mimosa advisory triage

Sealed deep scans are static and evidence-bounded: each advisory carries a proof gap
that only human triage closes. Triage for `marlonsc/mcb` follows rules D1–D5 of
`docs/adr/059-mimosa-advisory-triage-policy.md` in that repository. The summary below
routes; the ADR is the authority.

1. **Trust boundary (D1)** — an environment variable documented as an operator knob
   defines a boundary instead of escaping one. Triaging it means documenting the
   trust model per deployment surface, not inventing privilege boundaries.
2. **Sink containment (D2)** — a file-reading sink enforces canonical containment
   itself, skipping violations with a warning (never silently). Its test needs a
   demonstrated RED state, not only a green one.
3. **Fixture isolation (D3)** — code under vendored test fixtures is scan input, not
   production code. A cross-crate advisory with a fixture sink is a false positive
   when the fixture is outside every production dependency graph and the sink takes
   no external input; verify both structurally and record the evidence.
4. **Sentinels (D4)** — a client-replaced placeholder grants nothing; it is not a
   credential, but it must be a named, documented constant.
5. **Disposition ledger (D5)** — every disposition records the scan id, seal,
   structural evidence, decision rule, and landing reference on its bead. A
   re-reported anchor with a bead disposition closes by reference; only new anchors
   open new beads.
