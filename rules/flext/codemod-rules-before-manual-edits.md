---
description: codemod rules are the default correction mode in FLEXT projects
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-19","route:both"]'
---

# Codemod rules before manual edits

Operator law 2026-09-19 (flext-itpd1.3). A FLEXT correction must propagate to hundreds of
branches and projects; a manual edit is the same work redone thousands of times.

- The default correction mode is a rule in
  `flext-infra/src/flext_infra/codemod/rules/<id>.yml` (format of the existing rules:
  `id`, `language`, `severity`, `files`, `rule`, `fix`, `message`) applied to every
  occurrence at once by `make mod`. Imports, facades, aliases, signatures and repeated
  shapes are rewired this way, never site by site.
- A manual edit is the exception and requires a stated reason: the defect is genuinely
  unique, or the correct form cannot be expressed as an AST rewrite.
- A rule expresses the correct form. It never deletes information to silence a gate,
  and it constrains its receiver so legitimate homonyms keep their contract.
- Applied rules stay in the repository as the propagation contract for every other
  branch and project. A finding whose correction was done by hand where a rule was
  possible is a defect: write the rule and re-apply it.
- `make mod` answering `generated findings require canonical generator repair` names
  the generator as the owner; the rule then belongs in the template or planner, not in
  the generated files.
- Reuse before authoring: the existing catalog — the codemod rules directory and the
  fast global sed/ast-grep rules backported from `0.20.0-dev` — is searched first; a new
  rule is written only when no existing one expresses the form.
- Prefer the most general rule that still constrains its receiver; specialised rules
  are lost or bypassed in heavy refactors and must be justified.
- Before any heavy refactor (`make mod`, cascades, mass rewires) every project receives
  a fast checkpoint commit so a disaster returns in one step.
