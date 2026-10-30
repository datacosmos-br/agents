# Authoring ast-grep codemod rules

This reference covers rule anatomy, generalization and exactness for ast-grep YAML rules
and line-shaped text rules. The engine that runs them owns everything beyond the
ast-grep language: metadata keys, context predicates, receipts and Make verbs. For
FLEXT, read the workspace guide `docs/guides/codemod-rules.md`.

## Anatomy

```yaml
# Header comment: the law, why it holds, and every deliberate exclusion.
id: owner-verb-object            # unique across every layer the engine loads
language: Python
severity: error                  # a finding the gate blocks on
message: One sentence that names the correct form.
files:                           # scope; omit only when the law is truly global
  - "**/tests/**/*.py"
rule:                            # what matches (see Generalize and Exact)
  ...
constraints:                     # regex or kind limits on captured metavariables
  ...
transform:                       # derived text for the fix (replace, substring)
  ...
fix: |-                          # the correct form; omit for detection-only rules
  ...
```

The test file `<id>-test.yml` sits beside the catalog's other tests:

```yaml
id: owner-verb-object
valid:      # must NOT match: the correct form and every near miss you excluded
  - |
    ...
invalid:    # must match: every shape the law rejects
  - |
    ...
```

Snapshots record what each `invalid` case reports and how the fix rewrites it. Only
the repository's snapshot verb writes them.

## Generalize

Write the law once and let the variation live in the matcher.

**Alternatives instead of sibling rules.** Write one rule that matches every variant
with `any:`:

```yaml
rule:
  any:
    - pattern: assert $A == $B
    - pattern: assert $A != $B
```

**Constraints instead of literal copies.** Ten rules that ban ten library imports
become one rule:

```yaml
rule:
  kind: import_from_statement
  has: { field: module_name, pattern: $MOD }
constraints:
  MOD: { regex: '^(ldap3|oracledb|structlog|gitpython)(\.|$)' }
```

When an owner can derive the set (a package's declared facades, a dependency list), let
the engine's context predicate supply it instead of a regex list. A hand-maintained list
that duplicates a derivable set is itself a defect.

**Shared matchers instead of repeated guards.** A guard that several rules repeat, such
as "the module imports `tm` from its facade", goes to `utils/<name>.yml` once:

```yaml
- inside:
    kind: module
    stopBy: end
    has: { matches: tm-imported-from-flext, stopBy: end }
```

**Fixed-point bottom-up cascades for multi-step ladders.** When an engine repeats its
`ast-grep` catalog to a fixed point, a qualified rule may consume a terminal
guard/return pair and expose the preceding pair to the next pass. Prove the payload,
failure metadata, control flow and effects before choosing a Result operation; a
default-valued extraction must never hide failure. Reuse the engine's tested rules
and semantic witnesses rather than introducing another multi-statement AST walker.
Use a documented [syntax kind](https://ast-grep.github.io/reference/rule.html#kind)
or [metavariable](https://ast-grep.github.io/guide/pattern-syntax.html#meta-variable):
`kind: _` is not an any-node matcher. A cascade remains unqualified until its
declared catalog tests prove cardinality, near misses and fixed point.

**Context patterns for fragments.** Match a method, field or argument by giving the
pattern its enclosing syntax and selecting the node you mean:

```yaml
rule:
  pattern:
    context: |-
      class C:
          def $NAME($$$PARAMS) -> $RET:
              $$$BODY
    selector: function_definition
```

**Transforms for derived text.** Rewrite part of a capture without a second rule:

```yaml
transform:
  STATIC_PARAMS:
    replace: { source: $$$PARAMS, replace: '^self\s*,?\s*', by: '' }
```

## Exact

- **Anchor on syntax.** Use `kind` or `pattern` first. Use `regex` only to refine a
  node you already matched, never as the whole rule.
- **Scope with `files`.** A test-only law names the test trees. A rule without
  `files` must hold in every file the engine scans.
- **Bound relational searches.** `inside` and `has` stop at the direct relative by
  default. Add `stopBy: end` only when any ancestor or descendant qualifies. For
  "a method of a class", spell out the parent chain
  (`function_definition` inside `block` inside `class_definition`).
- **Exclude near misses with `not:`.** Name each exclusion in the header comment and
  cover it with a `valid` test case.
- **Keep the fix safe.**
  - The rewrite must preserve evaluation order and side effects.
  - It must only emit names that resolve; guard imports with a shared matcher.
  - It must be idempotent: its output must never match the rule again.
- **Text rules.**
  - Anchor with `^` and `$`, multiline flags and word boundaries.
  - Never let `.*?` cross a definition boundary.
  - Scope with `include`.
  - Name groups for the replacement.
  - Declare the exact expected count when the engine supports receipts.

## Increment instead of adding

When a new finding appears, check these before writing a new rule:

1. Does an existing rule state this law? Widen its `any:` or `constraints`.
2. Does an existing `utils/` matcher express the guard? Reference it.
3. Do several rules now differ only by literals? Merge them, then merge their tests and
   regenerate snapshots in the same change.
4. Is the new rule a one-shot migration of one symbol? Prefer the general law it is an
   instance of. If none exists, retire the migration under the repository's policy once
   it applies nothing anywhere it targets.

## Prototyping

Put draft cases in the engine's declared rule fixtures. Resolve native test, snapshot
and transformation operations from its catalog, then exercise those cases under the
real configuration. Review the snapshot and a second-run fixed point. The canonical
fixture and receipt owners preserve the evidence; do not create a scratch scanner,
copied tree or external script.
