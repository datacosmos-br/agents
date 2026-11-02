---
description: Rule exceptions are exterminated everywhere; only declared axioms survive, enforced by tooling
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-11-02","route:both"]'
---

# Rule exceptions are axioms only

Exterminating exceptions to rules is martial law, everywhere, for every session,
project and call (operator order 2026-11-02, tracker memory
`operator-order-2026-11-02-exceptions-martial-law`, verbatim excerpt: "isso não é regra,
é lei marcial"). Exceptions impede the stabilization and maintenance of code; anything
against this is exterminated at all costs and in every possible place.

The only surviving exceptions are axioms: what strict rules need in order to coexist
(tracker memory `operator-order-2026-11-02-exceptions-axioms-only`, verbatim excerpt:
"poquissimas excessoes controladas por tooling a mao de ferro"). An axiom is exactly one
of:

- enabling the project's declared model framework under the strict rules;
- resolving a conflict between lint or type tools;
- letting one pattern apply alongside another.

Each axiom is declared once in the project's tooling SSOT with its justification and is
enforced by that tooling; the tooling rejects every exception it does not declare. The
set stays tiny. Admitting an axiom is a rule change under
`rules/coordination/operator-precedence.md`, and no agent self-grants one.

Everything else is not an axiom and is exterminated at its root together with every
mechanism that honors it, in the same cutover under `rules/runtime/zero-residue.md`:

- member-level or per-file ignores;
- inline suppressions;
- code exemption mechanisms;
- docstring exemption markers;
- configuration exemption lists;
- rule carve-outs.

The permission dies with the hack: removing an exception while leaving the mechanism
that would honor the next one reopens the route. The violation the exception hid is
fixed at its owner, under `rules/architecture/engineering-core.md`.
