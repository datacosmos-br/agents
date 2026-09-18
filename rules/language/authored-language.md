---
description:
  All authored governance content is English-only, and knowledge stays hierarchical
  across layers.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-05","route:both"]'
---

# Authored language and layer hierarchy

Every authored artifact under the universal governance home and every project's
`.agents` tree is English-only: skills, rules, commands, agent profiles, references,
documentation, decision records, code comments, docstrings, log strings, templates, and
commit messages. Operator conversation may use any language; recorded artifacts may not.
Content in another language is a defect corrected at its owner in the same session,
never deferred.

The project's canonical law is the only authority that may declare a different authored
language. When a project declares one — for example Portuguese for `algar`, `gruponos`,
`cosmos-main`, and the other projects that declare it — every artifact it owns follows
that declared language: code comments, documentation, references, templates, commit
messages, and user-facing outputs. The declaration is singular and explicit; a project
without a declared authored language defaults to English-only. The universal governance
home itself is always English-only.

Knowledge stays hierarchical. Universal conduct, evidence, command selection, and
completion gates live in the global home. Technology and domain content lives in its
declared technology or domain layer. Framework and project deltas live only in the
owning project tree. Each layer references its parents and adds only its own delta; a
child strengthens its parents and never copies, weakens, renames, or replaces them. When
content appears at two layers, it moves to the highest applicable layer, consumers are
rewired to reference it there, and the duplicate is deleted in the same change.

A violation of language or placement blocks delivery until the owner is corrected, every
consumer is rewired, and the affected gates pass.
