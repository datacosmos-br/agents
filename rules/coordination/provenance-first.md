---
description: Provenance before conclusion
metadata:
  aihub.tags: '["decision:ADR-0007","effective:2026-09-03","route:both","supersedes:rule:coordination/provenance-before-conclusion"]'
---

# Provenance before conclusion

Before labeling silent or changed state as a defect, trace its actor, time, and
originating PR: `events.jsonl`, file mtimes, `git log -S` on the changed value, and
merged PRs in the window across every registered rig, not just the one that surfaced the
change. A state without a proven author is neither defect nor intention — it is
unproven, and stays unproven until one of the four sources names an actor and a time. A
rig's config changed by a merged cross-repo cutover PR is provenance, not silence;
correct the tracker item's premise instead of opening a defect against the receiving
project.

Evidence completeness follows the same law: a truncated read (`head -40` of
`make help`), a default-limited query, or a summarized listing proves a sample, never
the whole. Verify against the canonical source and the full command output before any
conclusion; what a partial read did not show stays unproven, and absence proved by it is
a false negative at the reader.

Compose with `tracker verification` (rule file).
