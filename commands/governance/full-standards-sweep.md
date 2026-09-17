---
name: full-standards-sweep
description: Sweep the hosted project to full governance standards and land the conformance result on the integration branch.
argument-hint: "<optional focus, scope, or project path>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-05","route:project"]'
---

# Full-standards cleanup and conformance sweep

Treat `$ARGUMENTS` as an optional focus. Resolve authority FIRST, before any
effect: workspace root `AGENTS.md`, then the branch-matched local law skill,
then the nearest scope `AGENTS.md`, then the active tracker item. Run
`make setup`, then use selector-free root Make verbs only. If the
rig hosts a third-party or non-framework project, apply only the universal
layers below and follow upstream conventions; never impose local architecture
there.

## Phase A — sweep the project

0b. Automation surfaces first. Drive classes with the declared machinery
   before hand edits: `make mod` applies the declared ast-grep rules
   (composed from installed distributions; targeted runs use an exact
   rule-ID filter, not ad-hoc CLI invocations); `make gen` twice
   brackets every generated-surface change and must be byte-identical; the
   persistent code-review-graph feeds discovery in CLI mode (`dead-code`,
   `impact`, `large-functions`, `query`) for nesting, callers, and split
   targets, operated per the `crg` skill (freshness gate and working-tree
   graph first). A violation class with no declared rule earns its rule at the
   highest applicable rule layer (universal for context-free patterns,
   framework for FLEXT deltas) in the same change; see
   `rules/workflow/structural-migrations.md` and
   `rules/workflow/mass-rewrite-discipline.md`.

0c. One class per boundary. Work violations by class wave; between waves run
   the incremental tests, commit the wave under the class name, and update
   the campaign tracker item. Mechanical waves (annotations, aliases)
   validate with the static-plus-runtime bracket; structural waves (nesting,
   facades) additionally re-run the integration gates before the next wave.

0. Declaration-first scoping and dependency freshness. Before consuming any
   error triage, declare the verification scan scope at the manifest SSOT
   (tests/scripts/docs are never production scope) and regenerate through
   the project generator, proving the conformance fixed point. Before any
   git-dependency pin or re-pin: fetch the remote branch, check whether
   commits touching the failing symbol already landed (the bug may be fixed
   upstream), install with `--no-cache`, and verify the bumped surface
   (`'field' in Model.model_fields`) before the first run. Identify which
   interpreter executes the dependency for the command at hand before
   touching any venv.
1. Truth with evidence, zero tolerance. Never lie, promise, or fabricate. A
   claim is true only with exact command, working directory, exit code,
   decisive output, and scope. Intention, self-report, and "mergeable" are not
   proof. Warnings, skips, empty output, and missing tools are RED; never
   normalize, cap, or suppress them. The first exception escapes with its raw
   traceback; no catch, retry, fallback, or normalization exists.
2. Canonical commands only. Everything runs through the declared Make
   dispatcher; invoke each verb directly. Never invent selectors,
   bypass with raw tools, or route around a broken verb:
   repair the verb at its owner, then rerun it. Diagnosis and validation obey
   the same rule as mutation.
3. Incremental test selection is mandatory. Every test execution keeps the
   canonical persistent test selection cache. The public full verb first runs
   the incremental verb, then testmon no-selection against the same database.
3b. Class-wave repair. When the measured report exceeds one screen (~20
   findings), work grouped by error class (defense-in-depth kill order:
   test-purity, aliases/owners, banned annotations, import-time wiring,
   silent failures, duplication, layout/loc), one root cause per commit,
   re-measure after each class, and record start→end numbers in the active
   plan or tracker item. Drive each wave through canonical owners: `make mod`
   for rule-driven codemods using the project rule SSOT, `make gen` for every
   generated-surface change, and code-review-graph evidence per the `crg`
   skill when available. Prove graph freshness with `build|update --repo`
   before `dead-code --json`, `impact --files`, or `query callers_of`; confirm
   every candidate in source. A false sweeping pass with a no-op bypass is
   never a "skip" — escalate.
4. Root cause, zero residue, complete rewire. Remove dead, superseded, and
   duplicate code in the same change; rewire every consumer to the final owner
   before the old one dies. No compatibility aliases, shims, dual paths,
   throwaway workarounds, or deferred defects. Pre-existing defects in the
   blast radius are adopted and fixed, never excused.
5. Reality is the authority; tests are never the source of truth. Tests
   validate observable behavior through public interfaces with maximum
   automation and typed shared fixtures. When tests contradict observed
   behavior, fix the tests. Hardcoded or non-automated test forms are
   blocking defects.
6. Architecture law. Apply the project's declared facade chain, module
   pattern, import direction, typing policy, dependency injection, and
   composition root exactly as its law states. Local redeclarations, aliases,
   competing layers, and direct hidden dependencies are removed on sight.
7. Disciplines in order per touched unit: discovery, necessity, single
   authority, responsibility boundaries, inline simplification, proven
   duplication removal, configuration ownership, and fail-loud error paths.
8. Generated surfaces and commit hygiene. Never hand-edit generated files;
   change the owner and regenerate, proving idempotence. Generated files keep
   their standardized header. Commits carry zero garbage; stage by explicit
   paths only; fix forward without destructive git operations; update docs in
   the same change as behavior.
8b. Mass-rewrite execution law. Tree-wide mechanical transformations and
   automation-apply cycles obey `rules/workflow/mass-rewrite-discipline.md`:
   test evidence brackets the mass (before and after), scoped commits bound
   the change per transformation class, applied-vs-reverted states are
   inventoried before commit, string literal contexts get a machine-checked
   safety sweep, and progress is reported per violation class, never as an
   aggregate that hides untouched structural debt. The sweep never parks a
   large uncommitted delta on the trunk.
9. Runtime boundary. Keep portable primitives in their reusable library and
   host indexes, daemons, forge clients, language/refactor services, hooks, and
   MCP in the runtime control plane. Cross that boundary only through a public
   command/hook/MCP. Absence of an optional unselected host is not an error and
   never authorizes a substitute; failure of a selected capability propagates.

## Phase B — align governance

Any rule, skill, command, document, decision record, template, hook, or
guidance that conflicts with, or fails to make explicit, the standards above is
corrected at its owner in this session. Keep knowledge hierarchical: universal
conduct stays in the global layer, technology content in its technology layer,
and framework deltas in the project layer; a child strengthens its parents and
never copies, weakens, or replaces them. Revalidate with the project's
advanced verification tooling and the duplication, single-authority, and
necessity methods.

## Phase C — land and propagate

Done means: full scope implemented, every declared gate green with the
declared mutation flag, zero residue, and the complete lifecycle recorded —
scoped commit, fast-forward push, resolved review, a no-fast-forward merge
into the declared integration branch, affected gates rerun on the merged
state, runtime proved on the integrated artifact, and release, deploy, and
activation each proven with distinct evidence. Local green, an open pull
request, or mergeable status is never landed. Stop only for a genuinely
destructive action or an authority conflict; ask one precise question; then
continue to full completion.
