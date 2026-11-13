# Authoring ast-grep codemod rules

This reference covers rule anatomy, generalization and exactness for ast-grep YAML rules
and line-shaped text rules. The engine that runs them owns its metadata keys and verbs;
for FLEXT, read the workspace guide `docs/guides/codemod-rules.md`.

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

The rule uses only what ast-grep sees in the file; nothing generates its patterns or
injects facts into it (`rules/law.md` 7).

**Shared matchers instead of repeated guards.** A guard that several rules repeat, such
as "the module imports `tm` from its facade", goes to `utils/<name>.yml` once:

```yaml
- inside:
    kind: module
    stopBy: end
    has: { matches: tm-imported-from-flext, stopBy: end }
```

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
  node you already matched, never as the whole rule. `kind: _` is not an any-node
  matcher; use a documented [syntax kind](https://ast-grep.github.io/reference/rule.html#kind)
  or [metavariable](https://ast-grep.github.io/guide/pattern-syntax.html#meta-variable).
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

## Prototyping

Put draft cases in the rule's own test file and run them through the repository's test
and snapshot verbs under the real configuration; no scratch scanner, copied tree or
external script stands in for them.
