---
description: FLEXT generators emit only what is declared; nothing is inferred, listed by hand, or accommodated
metadata:
  aihub.tags: '["decision:ADR-0024","effective:2026-09-20","route:both"]'
---

# Generator declarations law

Operator law 2026-09-20 (`flext-0in0k`). It binds every FLEXT generator, detector, and fix
(`make gen`, `make mod`, `make fix`, the namespace validator and its gates) and every
consumer of them: the FLEXT workspace family and every private workspace that
consumes the fleet toolchain, with their FLEXT subprojects. A generator that violates a
point below is defective at its owner; a consumer is never patched around it.

1. **The owner of a facade letter is the module that declares it** in its own explicit
   `__all__` — `models.py: __all__ = ["FlextApiModels", "m"]`. Ownership is never inferred
   from a filename. There is no closed set of letters: what the module declares is the
   whole truth.
2. **An `__init__.py` propagates; it never declares.** It emits what its sibling modules
   declare in their `__all__`, plus what the root exposes. Precedence: what the level
   itself declares wins; the rest comes from the root.
3. **The package root inherits from the main module; the root `__all__` overrides.** The
   root receives a letter from the module that declares it; a redeclaration in the root
   `__all__` prevails.
4. **Internal tiers are detected, never declared.** Every direct child folder of the
   repository root that contains Python code is a namespace. `src/` holds the **public**
   namespaces; every other folder is **always internal**. The manifest and the tooling
   are projected from that detection, with no list anywhere.
5. **Internal tiers inherit by class inheritance.** `tests/`, `examples/`, `scripts/` and
   any other internal folder inherit the root's short aliases. Their facade modules
   extend the root's by MRO — `class TestsFlextApiConstants(FlextApiConstants)` — and
   declare their own letter in their own `__all__`. Their init propagates. A
   subdirectory declares no short alias.
6. **The generator propagates; it never compensates.** If a module stops exporting its
   letter, the defect is the module's and the validator reports it. The generator never
   infers, fills in, or corrects.
7. **A violation is fixed at its source.** No guard, skip, exception list, or special
   case enters a generator to tolerate a file. A single case is exterminated at the
   source; a shape that can recur becomes a catalog rule with a fixture — the criterion
   is recurrence, not count.
8. **Verdict and count derive from one classification.** A gate fails on severity
   `error`; a warning is not a failure. There is no advisory-gate list by name.
9. **Every rule is computed from a source that already exists** and is **proven against
   the whole fleet before it is committed**. A rule that fires where it must not is a
   defect of the rule.
10. **Declaration adjustment is automatic; deriving beats listing.** Generators,
    decorators, and fixes are the official way to correct a project: when a declaration
    can be derived from an existing source (the module's `__all__`, the class base, the
    folder present on disk), the fix writes it — nobody types it. A closed list or an
    override is the last resort, only where no derivation exists; a list or rule that a
    derivation makes unnecessary is exterminated, never kept "for safety".
11. **Every module is one nested class.** A facade module declares exactly one top-level
    class, which nests its domain, and the letter in its `__all__`. Absolutely
    forbidden: manual redeclaration, an alias (short or long) outside `__all__`, a loose
    method, a loose function, an additional loose class. The existing FLEXT rules for
    this (one nested class per facade; `c/t/p/m/u` monopolize class declarations; no flat
    alias) are **absolute**: the finding is `error`, not warning; the correction belongs
    to the fix, not to a hand.
12. **An exception is the operator's decision, never the agent's.** There is no
    self-maintained exception list. Each surviving exception is a single motivated
    entry with a bead and the operator's deliberate, explicit authorization; without
    all four the exception does not exist and the case is a violation.
13. **A hack's permission dies with it.** Every exclusion, allowlist,
    `per-file-ignores`, validator bypass, advisory gate, single-file guard, or
    "tolerance" that **authorizes** a hack is exterminated in the same commit as the
    hack — it never survives empty.
14. **Every module obeys every rule, strictly, violating none.** The criterion is FLEXT +
    SOLID + DRY + YAGNI + Clean Architecture + SSOT + DI; any violation of any of them
    is a hack to exterminate. There is no separate "refactor" step: **strict compliance
    is the mechanism** — a module that follows every rule (one nested class, no alias,
    nothing loose, one owner, derivation, no duplicate) **deduplicates by itself**, and
    that is what frees the expected 60–80% of the current code with no loss of
    functionality. Applied by maximum automation (rope, ast-grep, generators, fixes)
    with minimum breakage; proven by before/after measurement and green gates.

Execution: one bead per phase under `flext-0in0k`, each carrying this text in full;
work in a worktree on the freshly fetched integration tip; extermination of lists and
their permissions before generator repair; never a rollback, never a manual mass fix.
Companion: `codemod-rules-before-manual-edits.md`.
