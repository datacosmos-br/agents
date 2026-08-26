---
name: pr-sheriff
description: "PR Sheriff patrol: discover open PRs across configured repos, triage into easy-wins / crew / human, merge easy-wins, dispatch reviews. USE FOR: periodic PR patrol duty on this town's repos. DO NOT USE FOR: implementing fixes yourself (sling a bead); posting to GitHub (output is inline; overseer posts)."
license: MIT
metadata:
  bundle: github
  scope: universal
---

# PR Sheriff

Delegates to the `mol-pr-sheriff-patrol` formula shared across rigs.

## Scope

Repos come from `$GT_ROOT/.beads/pr-sheriff-config.json` filtered to THIS town's rigs (`gt rig list`). Never scan or triage repos outside configured scope.

## Execution

1. `cat $GT_ROOT/.beads/pr-sheriff-config.json` — crew mappings, trust tiers.
2. `gt formula show mol-pr-sheriff-patrol` — follow steps in order: load-config → discover-prs → triage-batch → merge-easy-wins → dispatch-crew-reviews → dispatch-deep-reviews → collect-results → summarize.
3. Trust tiers from config: `bot-trusted` auto-merge on green CI; `community` normal triage; `firewalled` always NEEDS-HUMAN, never auto-merge.

## Triage tree

Draft → SKIP · firewalled → NEEDS-HUMAN · dependabot bump + CI green → EASY-WIN · <50 lines obvious fix → EASY-WIN · security/architecture/API or multi-concern → NEEDS-HUMAN · 100+ lines feature → NEEDS-CREW/HUMAN · else NEEDS-CREW.

## Dispatch beads

Fix-merge work for polecats uses **ephemeral wisps**, not persistent beads:
`bd new -t task "Fix PR #<n>: <desc>" -p 2 -l pr-review --wisp-type patrol`.

## Output

Per-PR block (category, 1–3 sentence analysis, recommendation) + patrol summary. Everything inline; nothing posted externally without the overseer.

## Critical rules

- Merge only easy-wins with green gates; everything else dispatches.
- Contributor-friendly: `Co-authored-by` trailer when fixing up contributor work.
