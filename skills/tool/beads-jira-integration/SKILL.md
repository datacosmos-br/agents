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
bd jira sync --push --state open --dry-run   # preview (state open is the default contract)
bd jira sync --push --state open --create-only  # create new issues only
bd jira sync --pull --state open             # pull status changes
bd jira sync --push --issues <id>,<id>       # selective push
```

The CLI writes `external_ref` on created beads; never set it manually.
`--parent <bead>` limits the push to one bead and its descendants; `--state`
defaults to `all` upstream — always pass `--state open` explicitly.

## Hierarchy Alignment

| Beads | Jira |
|---|---|
| feature (macro épico) | Task under Epic |
| task (child of feature) | Subtask under Task |
| bug | not pushed to Jira |

Epic key: `config.CosmosMain.jira.epic_key`.

## Sync Policy (beads is SSOT; Jira is a mirror of OPEN work)

- Only OPEN beads sync. Closed beads and `bug` type never create Jira issues.
- Re-push without dedup creates duplicate tickets: always `--dry-run` first,
  and keep `external_ref` as the single dedup key.
- A push that fails to write `external_ref` back leaves orphan Jira tickets
  the ledger cannot see — audit with
  `project = <KEY> AND parent IS EMPTY AND created >= "<sync-date>"`
  and transition strays to Done with a cause comment.
- The Jira API token is operator custody: it lives in `bd config`
  (or secret-tool at the service boundary), never in transcripts, git, or env
  files.

## Prohibited Patterns

- Jira REST calls outside `bd jira` or the FLEXT service (`urllib.request`,
  `requests`, `httpx` included).
- CSV data layers; data lives in beads; no superseded feature beads open; no
  hand-edited `custom.mk` with bead IDs or Jira keys.

Zero residue checklist: `references/procedure.md`.
