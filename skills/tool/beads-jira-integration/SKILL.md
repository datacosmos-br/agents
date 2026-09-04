---
name: beads-jira-integration
description: 'beads jira sync, epic link, flext service, native cli only'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:beads-jira","effective:2026-09-02","framework:flext","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:beads","updates:manual","usage:router"]'
---

# Beads Jira Integration

Activate when integrating beads with Jira Cloud. Sync goes through the native
`bd jira` CLI; the only custom code is the FLEXT `CosmosMainJiraService`
epic-link gap (`references/procedure.md`).

## Configuration (native `bd config`)

```bash
bd config set jira.url "https://<instance>.atlassian.net"
bd config set jira.project "<PROJECT_KEY>"
bd config set jira.push_prefix "<bead-prefix>"
bd config set jira.username "<email>"
bd config set jira.api_token "<token>"
```

The beads CLI owns all Jira credentials — never source, `.env`, project YAML,
or script env vars.

## Sync (native `bd jira sync`)

```bash
bd jira sync --push --dry-run      # preview
bd jira sync --push --create-only  # create new issues only
bd jira sync --pull                # pull status changes
```

The CLI writes `external_ref` on created beads; never set it manually.

## Hierarchy Alignment

| Beads | Jira |
|---|---|
| feature (macro épico) | Task under Epic |
| task (child of feature) | Subtask under Task |
| bug | not pushed to Jira |

Epic key: `config.CosmosMain.jira.epic_key`.

## Prohibited Patterns

- Jira REST calls outside `bd jira` or the FLEXT service (`urllib.request`,
  `requests`, `httpx` included).
- CSV data layers; data lives in beads; no superseded feature beads open; no
  hand-edited `custom.mk` with bead IDs or Jira keys.

Zero residue checklist: `references/procedure.md`.
