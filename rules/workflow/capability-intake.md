---
description: Canonical intake path for externally authored skills, commands, rules, and agent profiles — provenance, licensing, extends-based dedup, and short slugs at birth.
metadata:
  aihub.tags: '["decision:ADR-0014","effective:2026-09-07","route:project"]'
capsule_summary: |
  Externally authored capabilities enter the catalog only through a canonical
  change lane: frontmatter regenerated to grammar v2, license files shipped
  in-bundle with a provenance section in the body, overlap resolved as an
  extends: child carrying only its delta, byte-duplicates retired, and slugs
  kept to one or two words at birth. Project-tree downloads are staging
  material, never adoption; a second ad-hoc intake route is a violation.
---

# Capability intake

Nothing external enters the catalog by copy. Intake is a governed lane with
four obligations.

## Law

1. **Canonical format only.** Foreign frontmatter, category vocabularies, and
   multi-line description styles are replaced by the canonical grammar at
   intake. The original bundle stays readable, but the catalog record is
   canonical.
2. **Provenance ships in the bundle.** LICENSE files are preserved inside the
   skill directory; SKILL.md carries a provenance section naming origin,
   author, and license. Unlicensed material is either attributed in that
   section or rejected.
3. **Dedup through specialization.** A capability overlapping a canonical
   owner becomes a child with `extends:<owner>` and only delta content; the
   parent is never copied into the child. Subsumed artifacts — including
   unmanaged external copies in provider homes — are retired in the same
   change that adopts the canonical owner.
4. **Short slugs at birth.** One or two words, target ≤ 14 characters,
   family-consistent, catalog-unique. A slug that needs three words to be
   understood is renamed before landing, not after.

## Procedure

Inventory owner/consumers/overlap first (search-first), classify each
candidate as adopt / fold / retire, then land the whole set in one lane with
eval suites, gates green, and the retirement of every subsumed copy proven by
zero-residue search.
