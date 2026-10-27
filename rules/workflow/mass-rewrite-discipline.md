---
description:
  Tree-wide rewrites preserve shared work, inventory effects, and prove public behavior.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-25","route:both"]'
---

# Mass rewrite discipline: inventory, boundaries, evidence

Any transformation applied to more than a handful of files — textual rewrites
(`sed`/regex), ast-grep batch application, enforcer or codemod `apply` cycles, bulk
import/annotation migrations — is a production effect with the same standing as a code
change, not free bookkeeping. It is graded like code.

- **Test evidence brackets the rewrite.** The native catalog's test operation runs before
  the mass, as its
  baseline, and after it, not only after. The after-run is the single validation at the
  end of the cleanup order declared in `rules/architecture/engineering-core.md`; no
  heavy validation runs between extermination steps. Static gates green do not prove
  runtime: annotations evaluated by frameworks (pydantic, casts, generics), string
  literals, and fixtures can break only at runtime. A mass landing without a post-run
  test selection result is an unproved trunk.
- **Scoped evidence and landing.** Inventory relevant sources, hunks and dependencies
  while preserving concurrent WIP. Dirty or changing files require no clean-tree or
  checkpoint-commit prerequisite. Package complete validated transformations by owner,
  following `rules/git/gitflow-branch-pr.md` for publication and integration.
- **Inventory effects.** Record exactly which transformations applied and their current
  source state. Gate-dependent rollback is prohibited; repair failures forward at the
  owner under `rules/coordination/fix-forward-collaboration.md`. Unidentifiable mixed
  effects are defects, never permission to discard shared work.
- **Context-safety of the rewrite engine.** Textual substitution without
  annotation/string-context discrimination is suspect by default: a machine-checkable
  string-literal sweep over the touched tree is part of the change's proof, checked
  manually per suspect hit.
- **Conformance progress is reported by violation class.** Fixing the mechanical class
  (annotations, aliases) while structural classes (nesting, facades, module shape) stand
  untouched is not aggregate progress; declare counts per class, and let the structural
  classes own the remaining phase plan.
- **Tracker evidence cadence.** Each class landed updates the campaign tracker item in
  the same session with command, counts, and decisive output; a campaign without
  per-step tracker evidence is not a campaign.

Compose with `rules/workflow/structural-migrations.md` (rule layering),
`rules/workflow/production-readiness.md` (blast-radius adoption),
`rules/runtime/strict-execution.md` (atomic effects), and
the tracker-traceability rule (evidence cadence).

## Templates — surgery on managed templates (2026-09-11, from a real failure)

A managed template at its project-declared owner is production code with history.
Rewriting one from scratch is prohibited. Required:

1. **Surgical diff first**: remove only the blocks the transformation targets (defines,
   calls, conditionals). A rewrite from 732 to 467 lines destroyed the toolchain
   bootstrap, the caller's UV resolution, exports, and cygpath — about 400 cascading
   failures.
2. **Render context follows its schema**: every `{{ var }}` in a template must exist in
   its declared render model. Read that owner before referencing a variable. An error such as
   `'dict object' has no attribute 'X'` means an invented variable or a field removed
   from the SSOT.
3. **A render break is an owner symptom**: `{% if verb.requires_apply %}` referenced a
   field removed from `MakeVerbSpec`. Fixing the template is the extermination step
   itself; removing a field from the SSOT requires the template surgery in the same
   commit.
4. **A `.bak` inside `templates/` is a defect**: template discovery enumerates the
   directory. Staging follows its native owner and `rules/storage.md`.
5. **Distinguish an environment flag from a CLI argument**: the old environment flag
   that demanded confirmation was exterminated — every Make verb performs its operation
   directly, with no apply selector. CLI arguments belong to the current native command
   owner; resolve them there rather than copying names or treating them as Make selectors.
6. **Proof by rendering**: prove template changes through their native rendering and
   test operations to a fixed point, never by "it should render"; the run
   is the end-of-round validation of the cleanup order in
   `rules/architecture/engineering-core.md`.
