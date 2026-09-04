---
name: beads-jira-integration
description: 'beads jira sync, epic link, flext service, native cli only'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:beads-jira","effective:2026-09-02","framework:flext","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:beads","updates:manual","usage:router"]'
---

# Beads Jira Integration

Activate when integrating beads with Jira Cloud. Sync goes through the native
`bd jira` CLI; the only custom code is the FLEXT `CosmosMainJiraService`
epic-link gap. Read the `complete procedure` (skill file) before the first
push — it owns configuration, sync policy, credential custody, and the
recovery runbook.

## Sync (native `bd jira sync`)

```bash
bd jira sync --push --state open --dry-run      # preview; always first
bd jira sync --push --state open --create-only  # create new issues only
bd jira sync --pull --state open                # pull status changes
```

`--state` defaults to `all` upstream — always pass `--state open`. The CLI
writes `external_ref`, the only dedup key; never set it by hand and never
re-push without reviewing a dry run. The beads CLI owns every credential.

## Hierarchy Alignment

| Beads | Jira |
|---|---|
| feature (macro épico) | Task under Epic |
| task (child of feature) | Subtask under Task |
| bug | not pushed to Jira |

Epic key: `config.CosmosMain.jira.epic_key`. Only OPEN beads sync.

## Prohibited Patterns

- Jira REST calls outside `bd jira` or the FLEXT service (`urllib.request`,
  `requests`, `httpx` included).
- CSV data layers; data lives in beads; no superseded feature beads open; no
  hand-edited `custom.mk` with bead IDs or Jira keys.
