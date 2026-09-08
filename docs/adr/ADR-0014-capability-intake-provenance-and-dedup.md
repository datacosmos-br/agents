# ADR-0014: Capability intake is provenance-governed and deduplicated

Date: 2026-09-07
Status: Accepted
Rule: `rules/workflow/capability-intake.md`

## Context

On 2026-09-07 fifteen externally authored skills were measured sitting in
`~/flext/.agents/skills/` (flext commits `9fa1addc7`, `422b843af`): five
Anthropic-origin Apache-2.0 bundles, one Vercel guideline, two flext-native
skills, and seven individually authored customs, three of them without any
license. Their frontmatter follows foreign formats (multi-line descriptions,
`category: development`, no activation semantics), and several overlap with
canonical owners: `mcp-builder` vs `tool/mcp-patterns`,
`webapp-testing` vs `tool/playwright-e2e` and `tool/agent-browser`,
`skill-creator` vs `tool/skill-governance` plus an unmanaged external copy in
`~/.claude/skills/`, `ponytail` vs `project-wide/refactoring/yagni`, and
`flext-law`/`flext-context-routing` vs `framework/flext-development`.
Adopting them by copy would fork knowledge, import foreign metadata, and
route unvetted content to every project.

## Decision

Canonical adoption is the only intake path, and every adoption carries
provenance and dedup obligations:

1. **One lane, canonical format.** Intake lands through a change branch into
   this repository with canonical frontmatter, budgets, and an eval suite per
   skill. Foreign frontmatter is never preserved.
2. **Provenance lives in the bundle.** License files ship inside the skill
   directory; the SKILL.md body carries a short provenance section (origin,
   author, license). Unlicensed customs are adopted only with that
   attribution; otherwise they stay out.
3. **Overlap resolves through the specialization graph.** A capability that
   overlaps a canonical owner becomes a child with `extends:<owner>` and
   carries only its delta, referencing the parent. Byte-duplicates and
   subsumed artifacts are retired, never coexist. `flext-context-routing`
   folds into `flext-law`; the external `~/.claude/skills/skill-creator`
   copy is retired by the managed projection.
4. **Short slugs at birth.** New slugs use one or two words (target ≤ 14
   characters), match the family convention, and are unique across the
   catalog. Giant descriptive names are a defect at intake, not later.

## Consequences

- The catalog grows only through reviewed, attributed, deduplicated bundles;
  external downloads in project trees are staging, never adoption.
- Overlapping knowledge has exactly one owner; children stay delta-only, so
  parent evolution propagates without drift.
- The next intake repeats this path; a second ad-hoc adoption route is a
  violation of this ADR.
