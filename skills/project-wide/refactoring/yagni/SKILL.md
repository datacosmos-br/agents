---
name: yagni
description: "current consumers, speculative scope, deletion, zero residue"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","supersedes:skill:extermination-mode","usage:router"]'
  version: 2.0.0
---

# YAGNI

Code, options, settings, dependencies, abstractions and compatibility paths exist only
for a current consumer (`rules/law.md` laws 2 and 6). Having none is the evidence for
deletion, and a value that only repeats its owner's default goes too.

- Only deleting data, another repository's code or a published contract that outside
  consumers use waits for the operator. Law 11 protects another actor's work.
- Future need, symmetry, possible reuse and tests of the speculative code are not
  consumers; a current consumer, however rare, is.
- A removal takes its tests, fixtures, configuration, documentation and generated output
  in the same change; tests of behavior still required move to the replacing owner.
