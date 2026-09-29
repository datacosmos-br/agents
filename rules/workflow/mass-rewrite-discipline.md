---
description:
  Tree-wide mechanical rewrites and automation-applied fixes are commit-boundaried,
  inventories-first, and fully test-proven before and after.
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-09-29","route:both"]'
---

# Mass rewrite discipline: inventory, boundaries, evidence

Any transformation applied to more than a handful of files — textual rewrites
(`sed`/regex), ast-grep batch application, enforcer or codemod `apply` cycles, bulk
import/annotation migrations — is a production effect with the same standing as a code
change, not free bookkeeping. It is graded like code.

- **Test evidence brackets the rewrite.** `make test` runs before and after the mass,
  not only after. Static gates green do not prove runtime: annotations evaluated by
  frameworks (pydantic, casts, generics), string literals, and fixtures can break only
  at runtime. A mass landing without a post-run test selection result is an unproved
  trunk.
- **Commit boundaries are part of the change.** Never accumulate tree-wide uncommitted
  mass. Package the rewrite into scoped commits (owner of the transformation, not file
  adjacency) and push each package; a trunk with a large uncommitted delta has no
  identifiable state, no rollback, and blocks concurrent lanes.
- **Inventory the applied/reverted state.** Automation that applies and conditionally
  reverts per gate (enforcers, fixers) leaves mixed states. Before any commit, enumerate
  exactly what was applied and what was reverted per transformation, decide keep/revert
  per group, and propose the point fixed point. Uninventoryable apply/revert spray is a
  defect.
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

A managed template (`.j2` under `src/flext_infra/templates/`) is production code with
history, not scratch. Rewriting one from scratch is prohibited. Required:

1. **Surgical diff first**: remove only the blocks the transformation targets (defines,
   calls, conditionals). A rewrite from 732 to 467 lines destroyed the toolchain
   bootstrap, the caller's UV resolution, exports, and cygpath — about 400 cascading
   failures.
2. **Render context = RenderSpec fields**: every `{{ var }}` in a template must exist in
   its render model (for example `MakefileRenderSpec`). Read the model in
   `_models/config.py` before referencing a variable. An error such as
   `'dict object' has no attribute 'X'` means an invented variable or a field removed
   from the SSOT.
3. **A render break is an owner symptom**: `{% if verb.requires_apply %}` referenced a
   field removed from `MakeVerbSpec`. Fixing the template is the extermination step
   itself; removing a field from the SSOT requires the template surgery in the same
   commit.
4. **A `.bak` inside `templates/` is a defect**: template discovery enumerates the
   directory, and staging never lives in the repository.
5. **Distinguish an environment flag from a CLI argument**: the old environment flag
   that demanded confirmation was exterminated — every Make verb performs its operation
   directly, with no apply selector. `--apply`, an internal CLI argument of release,
   codegen init, and deps, is a distinct current internal contract: do not confuse it
   and do not remove it.
6. **Proof by rendering**: every template change runs the conform tests through the root
   `make test` verb until a fixed point, never "it should render".
