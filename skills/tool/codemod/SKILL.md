---
name: codemod
description:
  "ast-grep codemod rules, generalized law, exact matching, rule tests, snapshots, make verbs"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0038","detect:dependency:python:flext-infra","detect:marker:sgconfig.yml","effective:2026-11-03","route:project","subject:ast-grep","usage:on-demand"]'
---

# codemod

Author the ast-grep rules a repository applies through its declared verb (`make mod` in
FLEXT, whose workspace guide `docs/guides/codemod-rules.md` owns the engine's keys and
verbs). Each rule is one law, stated once, built only from what ast-grep sees, with its
test (`rules/law.md` 7). Anatomy and techniques: [authoring](references/authoring.md).

## Use for

- A violation, rewire or migration that more than one site shares.
- Widening a rule to a new variant of its law, or merging rules that state one law with
  different literals.

## Do not use for

- A unique edit at one site: fix it at its source.
- A finding inside a generated file: fix its generator.
- A law that needs facts ast-grep cannot see in the file: it is not an ast-grep rule.
- Applying rules outside the repository's declared verb.

## Outcomes

- An existing rule that states the law is widened instead of a sibling added; rules
  that differ only by literals become one rule with `constraints`, a repeated guard
  lives once in `utils/`, and a ban that shadows a rewrite is deleted.
- The rule sits at the highest layer where its law holds; a child layer only narrows.
- It is anchored on syntax and scoped with `files`. Every near miss is a `not:` clause
  with a `valid` case, and every rejected shape is an `invalid` case.
- Snapshots change only through the repository's snapshot verb, reviewed in the same
  commit.
- Applying the rule a second time changes nothing, and the affected tests pass.
- A superseded law, or a migration that no longer matches anything, leaves with its rule,
  test and snapshot in the same change.

Record the rule id, the verb, its applied counts and the test result on the change.
