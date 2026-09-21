# ADR-0024 — FLEXT generator declarations law

**Status:** Accepted **Date:** 2026-09-20 **Scope:** the rule
`rules/flext/generator-declarations.md`, every FLEXT generator, detector and fix
(`make gen`, `make mod`, `make fix`, the namespace validator and its gates), and every
consumer of them across the governed fleet

## Context

The operator ruled on 2026-09-20 (`flext-0in0k`) how FLEXT generators may derive what
they emit. The rule was landed in this repository by PR #163 with the approval tag
`decision:ADR-018`, borrowing the three-digit record numbering of the flext repository.
This repository's approval owner accepts only a four-digit record that resolves
physically into `docs/adr/`; the only record numbered 018 here governs an unrelated
subject, the 0.5.0 release line. The tag therefore failed validation, and because the
installed governance bundle is preflighted before every projection, one malformed tag
stopped this repository's own gate and every governance deployment that consumes the
bundle.

The validator is correct. What was missing was the record the rule points at.

## Decision

This record is that decision, and the rule carries `decision:ADR-0024`.

A FLEXT generator emits only what is declared, and derives a declaration rather than
listing it wherever a source already exists. The normative text is the rule itself; the
substance it binds is:

1. The owner of a facade letter is the module that declares it in its own explicit
   `__all__`. Ownership is never inferred from a filename, and there is no closed set of
   letters.
2. An `__init__.py` propagates what its siblings declare; it never declares. The package
   root inherits from its main module, and a redeclaration in the root `__all__` wins.
3. Internal tiers are detected from the directories present on disk, never declared in a
   list, and they inherit the root's aliases by class inheritance.
4. The generator propagates and never compensates. A module that stops exporting its
   letter is the defect, reported by the validator; no guard, skip, exception list or
   special case enters a generator to tolerate a file. A shape that can recur becomes a
   catalogue rule with a fixture.
5. Verdict and count derive from one classification: a gate fails on severity `error`
   and a warning is not a failure.
6. Every rule is computed from a source that already exists and is proven against the
   whole fleet before it is committed. Declaration adjustment is automatic: when a
   declaration can be derived, the fix writes it and nobody types it.
7. Every facade module is one nested class.

The tag grammar is unchanged: a decision reference is a four-digit record in this
repository's `docs/adr/`, and a rule written from another repository's ruling is
recorded here before it can cite that ruling. The validator is not relaxed to accept a
foreign numbering.

## Consequences

- `rules/flext/generator-declarations.md` validates, the bundle preflight passes again,
  and governance deployments that consume the bundle resume.
- Any future rule imported from a FLEXT ruling carries a record in this repository
  first; the ruling's own identifier (here `flext-0in0k`) is cited in the record's
  context, not in the tag.
- A generator that violates a point above is defective at its owner; a consumer is
  never patched around it.
