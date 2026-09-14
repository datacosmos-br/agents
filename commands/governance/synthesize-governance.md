---
name: synthesize-governance
description: Synthesize an external governance corpus into current canonical owners without copying its structure.
argument-hint: "<source corpus and requested governance outcome>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:project"]'
---

# Synthesize governance

Treat `$ARGUMENTS` as one explicit source corpus and the requested governance
outcome. Refuse an absent, unreadable, symlinked, ownership-ambiguous, or
unbounded source, or a target whose canonical governance owners cannot be
resolved.

1. Read the target instructions, semantic artifact contracts, public bundle,
   ownership map, evaluations, root Make surface, and current consumers.
2. Inspect the complete relevant source bundles, including references, scripts,
   assets, manifests, provenance, license, generated state, and executable
   effects. Historical presence is evidence, never authority or permission.
3. Derive each behavior's outcome, trigger, non-trigger, inputs, effects,
   failure contract, scope, consumer, and proof. Classify it as already owned,
   an extension of one current owner, a distinct required capability, or
   rejected residue.
4. Place mandatory invariants in rules, conditional procedures in skills,
   explicit invocation grammar in commands, and discovery metadata in agents or
   config. AI Hub alone maps the released bundle into runtime and provider
   delivery. Split mixed sources and reference owners instead of concatenating
   prose.
5. Change only canonical owners. Rewire every current consumer and update
   semantic suites, guarantee mapping, documentation, and the public bundle
   atomically. Remove superseded canonical identities in the same cutover; never
   modify or delete the supplied source corpus.
6. Run `make runtime`, `make check`, `make test`, and
   `make test-full`, then search for duplicate owners, aliases, foreign
   runtimes, private paths, compatibility, fallback, retry, and stale consumers.

Return the source and target identities, semantic classifications, selected
owners, rejected behavior with reasons, consumer rewiring, exact runtime and
gate evidence, downstream AI Hub consumer contract, and first blocker. Do not
report file counts or non-empty output as semantic success.
